"""One-shot setup — pull everything the radar needs, no manual steps.

Whisper runs fully on-device (free, no API key). The only cost is a one-time
model download the first time you transcribe. This script does that download
up front so the first real run isn't slow, and installs faster-whisper if it's
missing.

    python3 -m radar.setup            # install + pre-pull the default model
    python3 -m radar.setup --model medium
    python3 -m radar.setup --check    # just report status, install nothing
"""
import argparse, importlib.util, subprocess, sys


def _have(mod: str) -> bool:
    return importlib.util.find_spec(mod) is not None


def _pip_install(pkg: str) -> bool:
    print(f"→ installiere {pkg} …", file=sys.stderr)
    r = subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", pkg])
    return r.returncode == 0


def ensure(model_size: str = "small", check_only: bool = False) -> bool:
    ok = True

    if not _have("faster_whisper"):
        if check_only:
            print("faster-whisper: FEHLT (python3 -m radar.setup)")
            return False
        ok = _pip_install("faster-whisper")
        if not ok:
            print("Konnte faster-whisper nicht installieren.", file=sys.stderr)
            return False
    else:
        print("faster-whisper: ok")

    if check_only:
        print(f"Whisper-Modell '{model_size}' wird beim ersten Lauf geladen, falls nötig.")
        return ok

    # Pre-pull the model by instantiating it once (download is cached in ~/.cache).
    print(f"→ lade Whisper-Modell '{model_size}' (einmalig, wird gecacht) …", file=sys.stderr)
    from faster_whisper import WhisperModel
    WhisperModel(model_size, device="cpu", compute_type="int8")
    print(f"Whisper-Modell '{model_size}': ok")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="small",
                    help="tiny|base|small|medium (Standard: small)")
    ap.add_argument("--check", action="store_true", help="nur Status, nichts installieren")
    a = ap.parse_args()
    ok = ensure(a.model, check_only=a.check)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
