#!/usr/bin/env python3
"""Transcribe all Pat Fleet audio clips using faster-whisper."""

import os, json
from pathlib import Path
from faster_whisper import WhisperModel

AUDIO_DIR = Path(__file__).parent / "pa"
OUT_FILE  = Path(__file__).parent / "transcripts.json"

SUBDIRS = {"digits","letters","phonetic","ha","wx","silence","dictate","followme"}


def scan_clips():
    """Return {clip_name: abs_path} for every wav file, mirroring assembler.py logic."""
    found = {}

    def add(name, path):
        if name in found and not str(path).endswith(".ulaw.wav"):
            return
        found[name] = path

    for entry in sorted(AUDIO_DIR.iterdir(), key=lambda e: e.name):
        if entry.is_dir() and entry.name in SUBDIRS:
            subdir = entry.name
            for f in sorted(entry.iterdir(), key=lambda e: e.name):
                if not f.name.endswith(".wav"):
                    continue
                stem = f.name[:-9] if f.name.endswith(".ulaw.wav") else f.name[:-4]
                add(subdir + "/" + stem, f)
        elif entry.is_file() and entry.name.endswith(".wav"):
            stem = entry.name[:-9] if entry.name.endswith(".ulaw.wav") else entry.name[:-4]
            add(stem, entry)

    return found


def main():
    print("Loading Whisper base model…")
    model = WhisperModel("base", device="cpu", compute_type="int8")

    clips = scan_clips()
    total = len(clips)
    print(f"Found {total} clips total\n")

    existing = {}
    if OUT_FILE.exists():
        existing = json.loads(OUT_FILE.read_text())

    results = dict(existing)
    new_count = 0

    for i, (name, path) in enumerate(sorted(clips.items()), 1):
        if name in results:
            continue

        try:
            segments, _ = model.transcribe(
                str(path),
                language="en",
                beam_size=3,
                vad_filter=True,
                vad_parameters={"min_silence_duration_ms": 200},
            )
            text = " ".join(s.text.strip() for s in segments).strip()
        except Exception as e:
            text = ""
            print(f"  ERROR {name}: {e}")

        results[name] = text
        new_count += 1

        print(f"  [{new_count} new]  {name!r} → {text!r}")

        if new_count % 50 == 0:
            OUT_FILE.write_text(json.dumps(results, indent=2, sort_keys=True))

    OUT_FILE.write_text(json.dumps(results, indent=2, sort_keys=True))
    print(f"\nDone. {new_count} new transcripts, {len(existing)} already cached.")
    print(f"Total: {len(results)} in {OUT_FILE}")


if __name__ == "__main__":
    main()
