# -*- coding: utf-8 -*-
"""The lesson's voice from the SME's recorded WAVs: trim, level, write (the reference lesson's method —
HI02H11_L02_S02 1_SPEC/prepare_lesson_voice.py).

Source : assets/Audio/voiceovers/<Audio ID>.wav   (one per clip, named by Audio ID — not shipped)
Output : assets/Audio/<Audio ID>.ogg              (the file the game plays)
The Gemini TTS takes these replace are in git history (commit before this round).

Per clip:
  trim   - dead air off both ends (below -45 dBFS), keeping 30 ms before the voice and 120 ms after it,
           so a line starts the moment the page asks for it (Swiftee's lip-sync and the transition
           titles are timed from the clip's start)
  level  - to -16 LUFS integrated; a look-ahead peak limiter at -1 dBFS (at most 6 dB of limiting)
  write  - 16-bit PCM WAV, mono, 24 kHz, under the .ogg name the game uses (the builder reads these as
           WAV to measure the lip-sync, the title cues and the ₹10 / ₹1 / total highlights)

Run:  PYTHONUTF8=1 python scripts/prepare_vo.py [clip_id ...]   then rebuild
      (PYTHONUTF8=1 python scripts/build_skill_MTG2A04_L01_S01.py, then scripts/make_dist.py)
"""
import os, re, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "assets", "Audio", "voiceovers")
OUT = os.path.join(ROOT, "assets", "Audio")
TARGET, PEAK_MAX = -16.0, -1.0
TRIM = ("silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.03,"
        "areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.12,areverse")

def ff(args):
    return subprocess.run(["ffmpeg", "-hide_banner", "-nostats"] + args, capture_output=True, text=True).stderr

def measure(path, pre=""):
    # padded with silence: a clip under 0.4 s is shorter than one loudness block and would read as -70 LUFS
    af = (pre + "," if pre else "") + "apad=pad_dur=1,ebur128=peak=sample,volumedetect"
    e = ff(["-i", path, "-af", af, "-f", "null", "-"])
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", e)[-1]), float(re.findall(r"max_volume: (-?[\d.]+) dB", e)[-1])

def main():
    wavs = sorted(f for f in os.listdir(SRC) if f.lower().endswith(".wav"))
    only = set(sys.argv[1:])
    if only: wavs = [f for f in wavs if os.path.splitext(f)[0] in only]
    if not wavs: sys.exit("no WAVs in " + SRC)
    for f in wavs:
        cid = os.path.splitext(f)[0]
        src = os.path.join(SRC, f)
        lufs, peak = measure(src, TRIM)
        gain = min(TARGET - lufs, PEAK_MAX - peak + 6.0)
        dst = os.path.join(OUT, cid + ".ogg")
        ff(["-y", "-i", src, "-af", "%s,volume=%.2fdB,alimiter=limit=%.4f:attack=2:release=40:level=disabled"
            % (TRIM, gain, 10 ** (PEAK_MAX / 20)), "-ac", "1", "-ar", "24000", "-c:a", "pcm_s16le", "-f", "wav", dst])
        l2, p2 = measure(dst)
        d0 = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src],
                                  capture_output=True, text=True).stdout)
        d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", dst],
                                 capture_output=True, text=True).stdout)
        print("  %-18s %5.2f -> %5.2f s   %6.1f -> %6.1f LUFS   peak %5.1f dBFS" % (cid, d0, d, lufs, l2, p2))
    print("  %d clips written to %s" % (len(wavs), OUT))

if __name__ == "__main__":
    main()
