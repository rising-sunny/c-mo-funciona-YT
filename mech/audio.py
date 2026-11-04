"""Audio procedural (sin muestras con copyright): música de fondo, efectos y mezcla con la narración."""
import os
import numpy as np
import soundfile as sf

SR = 24000
rng = np.random.default_rng(7)


def _env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(t / max(a, 1e-4), 1.0) * np.exp(-t / d)


def whoosh(dur=0.6):
    n = int(dur * SR)
    noise = rng.standard_normal(n)
    out, y = np.zeros(n), 0.0
    for i in range(n):                       # paso bajo de un polo con barrido de frecuencia
        alpha = 0.03 + 0.42 * np.sin(np.pi * i / n) ** 2
        y += alpha * (noise[i] - y)
        out[i] = y
    env = np.sin(np.pi * np.arange(n) / n) ** 2
    return (out * env * 2.2).astype(np.float32)


def thunk():
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    body = np.sin(2 * np.pi * (95 * np.exp(-t * 9) + 38) * t) * np.exp(-t * 11)
    click = rng.standard_normal(n) * np.exp(-t * 90) * 0.5
    return (body + click).astype(np.float32)


def tick():
    n = int(0.03 * SR)
    t = np.arange(n) / SR
    return (np.diff(rng.standard_normal(n + 1)) * np.exp(-t * 160) * 0.5).astype(np.float32)


def blip(f0=700, f1=1250):
    n = int(0.14 * SR)
    t = np.arange(n) / SR
    f = f0 + (f1 - f0) * (t / t[-1])
    return (np.sin(2 * np.pi * f * t) * np.exp(-t * 22)).astype(np.float32)


def place(track, clip, t, gain=1.0):
    i = int(t * SR)
    if i < 0 or i >= len(track):
        return
    seg = clip[: len(track) - i]
    track[i:i + len(seg)] += seg * gain


def music(dur, bpm=104):
    """Base alegre y ligera: bajo, arpegio pulsado, bombo suave y hi-hat. Progresión Am-F-C-G."""
    n = int(dur * SR)
    out = np.zeros(n, dtype=np.float32)
    beat = 60.0 / bpm
    roots = [220.0, 174.61, 261.63, 196.0]            # La, Fa, Do, Sol
    triads = [(1, 1.2, 1.5), (1, 1.26, 1.5), (1, 1.26, 1.5), (1, 1.26, 1.5)]
    triads[0] = (1, 1.1892, 1.4983)                    # menor
    nb = int(dur / beat) + 2
    for b in range(nb):
        t0 = b * beat
        chord = (b // 4) % 4
        root = roots[chord] / 2
        # bombo
        if b % 1 == 0:
            n_k = int(0.25 * SR)
            tk = np.arange(n_k) / SR
            kick = np.sin(2 * np.pi * (110 * np.exp(-tk * 22) + 42) * tk) * np.exp(-tk * 9) * 0.55
            place(out, kick.astype(np.float32), t0)
        # hi-hat en contratiempos
        place(out, tick() * 0.5, t0 + beat / 2)
        # bajo en corcheas
        for h in range(2):
            tb = t0 + h * beat / 2
            m = int(beat / 2 * SR)
            tt = np.arange(m) / SR
            f = root * (2 if (b + h) % 4 == 3 else 1)
            bass = (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(2 * np.pi * 2 * f * tt)) * np.exp(-tt * 7) * 0.32
            place(out, bass.astype(np.float32), tb)
        # arpegio en semicorcheas
        for q in range(4):
            tq = t0 + q * beat / 4
            tone = roots[chord] * triads[chord][(b * 4 + q) % 3] * (2 if (q % 2) else 1)
            m = int(0.22 * SR)
            tt = np.arange(m) / SR
            pluck = (np.sin(2 * np.pi * tone * tt) + 0.4 * np.sin(2 * np.pi * 2 * tone * tt)) * np.exp(-tt * 14) * 0.16
            place(out, pluck.astype(np.float32), tq)
    fade = np.ones(n, dtype=np.float32)
    fi, fo = int(0.6 * SR), int(1.8 * SR)
    fade[:fi] = np.linspace(0, 1, fi)
    fade[-fo:] = np.linspace(1, 0, fo)
    return out * fade


def mix(spec, narr_dir, out_wav):
    total = spec.total_duration() + 0.4
    n = int(total * SR)
    narr = np.zeros(n, dtype=np.float32)
    sfx = np.zeros(n, dtype=np.float32)
    wh = whoosh()
    for i, s in enumerate(spec.SCENES):
        t0 = spec.scene_start(i)
        w, sr = sf.read(os.path.join(narr_dir, f"narration_{s['id']}.wav"), dtype="float32")
        place(narr, w, t0)
        if i > 0:
            place(sfx, wh, t0 - 0.25, 0.30)
        if s["eq"]:
            nw = len(s["title"].split())
            place(sfx, blip(), t0 + 0.30 + 0.085 * nw + 0.25, 0.20)
    place(sfx, thunk(), spec._at("close", 0.82) + 0.05, 0.9)
    tk, prev = tick(), None
    for step in range(int(total * 200)):                         # clics de trinquete cada 1/8 de vuelta
        t = step / 200
        q = int(spec.turns_at(t) * 8)
        if prev is not None and q != prev:
            place(sfx, tk, t, 0.35)
        prev = q
    mus = music(total)
    # reducción automática del volumen de la música bajo la voz (sidechain simple)
    k = int(0.06 * SR)
    env = np.convolve(np.abs(narr), np.ones(k) / k, mode="same")
    duck = 1.0 - 0.62 * np.clip(env / 0.05, 0, 1)
    duck = np.convolve(duck, np.ones(int(0.12 * SR)) / int(0.12 * SR), mode="same")
    mus = mus * duck * 0.30
    voice = narr * 0.95
    out = voice + mus + sfx * 0.9
    peak = np.max(np.abs(out))
    if peak > 0.95:
        out = out * (0.95 / peak)
    sf.write(out_wav, out, SR)
    return out_wav
