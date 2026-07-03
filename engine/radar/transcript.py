"""Transcript — pull a video's own captions via yt-dlp (free, no STT costs).

TikTok auto-generates captions for most spoken-word videos and yt-dlp exposes
them as VTT. We take any available language (creator misinfo is usually in the
preset's language anyway) and flatten the VTT to clean text with timestamps.

If a video has NO captions, we mark it "no_transcript" instead of guessing —
the skill surfaces those for manual review rather than fact-checking silence.
(Optional Whisper fallback is documented in the skill, not required.)
"""
import subprocess, re, os, glob, tempfile


def _clean_vtt(path: str) -> list:
    """VTT -> [(start_seconds, text), ...] deduplicated."""
    lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
    cues, cur_t = [], None
    for ln in lines:
        m = re.match(r"(\d+):(\d+):(\d+)\.\d+\s+-->", ln) or re.match(r"(\d+):(\d+)\.\d+\s+-->", ln)
        if m:
            g = [int(x) for x in m.groups()]
            cur_t = g[0] * 3600 + g[1] * 60 + g[2] if len(g) == 3 else g[0] * 60 + g[1]
            continue
        ln = re.sub(r"<[^>]+>", "", ln).strip()
        if not ln or ln == "WEBVTT" or ln.isdigit() or "-->" in ln:
            continue
        if cues and cues[-1][1] == ln:
            continue
        cues.append((cur_t or 0, ln))
    return cues


def fetch_transcript(url: str, timeout: int = 120, lang_preference: list = None) -> dict:
    """Return {ok, lang, text, cues:[(t,line)...]} or {ok:False, reason}.

    lang_preference: ordered lang-code prefixes to prefer (e.g. ["deu", "de"]).
    TikTok often ships the ORIGINAL captions plus a machine-translated eng-US
    track — for non-English creators the translation is garbled, so preferring
    the original language matters for quotable claims.
    """
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "v")
        p = subprocess.run(
            ["yt-dlp", "--skip-download", "--write-subs", "--write-auto-subs",
             "--sub-langs", "all", "--sub-format", "vtt",
             "--socket-timeout", "30", "-o", out, url],
            capture_output=True, text=True, timeout=timeout,
        )
        vtts = glob.glob(out + "*.vtt")
        if not vtts:
            reason = "no_captions"
            if p.returncode != 0 and p.stderr.strip():
                reason = p.stderr.strip().splitlines()[-1]
            return {"ok": False, "reason": reason}

        def _lang(path):
            m = re.search(r"\.([A-Za-z-]+)\.vtt$", path)
            return (m.group(1) if m else "unknown").lower()

        path = vtts[0]
        for pref in (lang_preference or []):
            hit = next((v for v in vtts if _lang(v).startswith(pref.lower())), None)
            if hit:
                path = hit
                break
        lang = re.search(r"\.([A-Za-z-]+)\.vtt$", path)
        cues = _clean_vtt(path)
        return {
            "ok": True,
            "lang": lang.group(1) if lang else "unknown",
            "cues": cues,
            "text": " ".join(t for _, t in cues),
        }
