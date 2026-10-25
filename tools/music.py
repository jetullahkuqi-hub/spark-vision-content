"""Original royalty-free background loop for Reels (soft pad + bass + kick + hat).
`seed` picks tempo and chord progression so consecutive Reels don't sound identical."""
import numpy as np, wave

SR = 44100
PROGRESSIONS = [  # (chord tones Hz, bass Hz) per bar
    [((220.0, 261.63, 329.63), 110.0), ((174.61, 220.0, 261.63), 87.31), ((130.81, 196.0, 261.63), 65.41), ((196.0, 246.94, 293.66), 98.0)],
    [((146.83, 174.61, 220.0), 73.42), ((116.54, 146.83, 174.61), 58.27), ((130.81, 164.81, 196.0), 65.41), ((110.0, 130.81, 164.81), 55.0)],
    [((164.81, 196.0, 246.94), 82.41), ((130.81, 164.81, 196.0), 65.41), ((146.83, 185.0, 220.0), 73.42), ((123.47, 146.83, 185.0), 61.74)],
    [((196.0, 233.08, 293.66), 98.0), ((155.56, 196.0, 233.08), 77.78), ((174.61, 220.0, 261.63), 87.31), ((146.83, 174.61, 220.0), 73.42)],
]

def _pad(f, dur):
    t = np.arange(int(dur * SR)) / SR
    s = sum(np.sin(2 * np.pi * f * d * t) for d in (1.0, 1.003, 0.997)) / 3 + 0.25 * np.sin(4 * np.pi * f * t)
    return s * np.minimum(1, t / 0.4) * np.minimum(1, (dur - t) / 0.5)

def _kick(dur=0.35):
    t = np.arange(int(dur * SR)) / SR
    ph = 2 * np.pi * np.cumsum(110 * np.exp(-t * 18) + 45) / SR
    return np.sin(ph) * np.exp(-t * 9)

def _hat(rng, dur=0.06):
    n = np.diff(rng.standard_normal(int(dur * SR)), prepend=0)
    return n * np.exp(-np.arange(n.size) / SR * 70) * 0.25

def track(total, seed=0):
    rng = np.random.default_rng(seed)
    bpm = [92, 100, 108, 96][seed % 4]
    prog = PROGRESSIONS[(seed // 4) % len(PROGRESSIONS)]
    beat = 60 / bpm; bar = beat * 4
    out = np.zeros(int((total + bar + 1) * SR))
    i, t0 = 0, 0.0
    while t0 < total:
        ch, bass = prog[i % 4]
        seg = sum(_pad(f, bar) for f in ch) / 3 * 0.32 + _pad(bass, bar) * 0.28
        a = int(t0 * SR); out[a:a + seg.size] += seg
        for k in range(4):
            tb = t0 + k * beat
            kk = _kick() * (0.55 if k % 2 == 0 else 0.4)
            s = int(tb * SR); out[s:s + kk.size] += kk
            hh = _hat(rng); s2 = int((tb + beat / 2) * SR); out[s2:s2 + hh.size] += hh
        i += 1; t0 += bar
    out = out[: int(total * SR)]
    t = np.arange(out.size) / SR
    out *= np.minimum(1, t / 0.3) * np.minimum(1, (total - t) / 1.2)
    return out / (np.max(np.abs(out)) + 1e-9) * 0.8

def write(path, total, seed=0):
    x = track(total, seed)
    pcm = (np.stack([x, x], axis=1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
