"""Narración con Kokoro (TTS local, Apache-2.0): audio por plano + tiempos por frase y por palabra."""
import json, os, re
import numpy as np
import soundfile as sf

MODEL = ".models/kokoro-v1.0.int8.onnx"
VOICES = ".models/voices-v1.0.bin"
SR = 24000
LEAD, TAIL, MIN_GAP = 0.30, 0.55, 0.14


def _trim(a, thr=0.012, margin=0.03):
    idx = np.where(np.abs(a) > thr)[0]
    if len(idx) == 0:
        return a
    lo, hi = max(0, idx[0] - int(margin * SR)), min(len(a), idx[-1] + int(margin * SR))
    return a[lo:hi]


def split_sentences(text):
    parts = re.findall(r"[^.?!…]+(?:\.\.\.|[.?!…])+|[^.?!…]+$", text.strip())
    return [p.strip() for p in parts if p.strip()]


def word_times(sentence, start, dur):
    """Reparte la duración de la frase entre sus palabras según longitud (+ pausa tras puntuación)."""
    words = sentence.split()
    w = [len(re.sub(r"\W", "", x)) + 1.5 + (2.0 if re.search(r"[,;:…]|\.\.\.", x) else 0) for x in words]
    tot, t, out = sum(w), start, []
    for x, wi in zip(words, w):
        d = dur * wi / tot
        out.append(dict(w=x, start=round(t, 3), end=round(t + d, 3)))
        t += d
    return out


def build(spec, out_dir, voice="am_puck", speed=1.05, lang="en-us"):
    from kokoro_onnx import Kokoro
    k = Kokoro(MODEL, VOICES)
    os.makedirs(out_dir, exist_ok=True)
    timing = {}
    for sc in spec.SCENES:
        chunks, lines, t = [], [], LEAD
        for sent in split_sentences(sc["say"]):
            a, sr = k.create(sent, voice=voice, speed=speed, lang=lang)
            assert sr == SR
            a = _trim(a)
            d = len(a) / SR
            lines.append(dict(text=sent, start=round(t, 3), end=round(t + d, 3), words=word_times(sent, t, d)))
            gap = MIN_GAP + (0.12 if sent[-1] in "?!" else 0.0)
            chunks.append((t, a))
            t += d + gap
        speech_end = lines[-1]["end"]
        dur = max(sc["dur"], speech_end + TAIL)
        track = np.zeros(int(dur * SR) + 1, dtype=np.float32)
        for off, a in chunks:
            i = int(off * SR)
            track[i:i + len(a)] += a
        sf.write(os.path.join(out_dir, f"narration_{sc['id']}.wav"), track, SR)
        timing[sc["id"]] = dict(dur=round(dur, 3), lead=LEAD, lines=lines)
        print(f"{sc['id']:7s} speech {speech_end:5.2f}s -> plano {dur:5.2f}s", flush=True)
    path = os.path.join(os.path.dirname(spec.__file__), "timing.json")
    json.dump(timing, open(path, "w"), indent=1, ensure_ascii=False)
    return timing
