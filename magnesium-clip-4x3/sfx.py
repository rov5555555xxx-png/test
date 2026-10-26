# Synthesizes the sound-effect track for the clip; cue times match the animation delays in index.html.
import sys, wave, numpy as np
SR = 44100
DUR = float(sys.argv[2])
rng = np.random.default_rng(7)
out = np.zeros(int(SR * (DUR + 2)))

def t_(d): return np.arange(int(SR * d)) / SR
def env(n, a=0.005, r=None):
    e = np.ones(n); k = max(1, int(SR * a)); e[:k] = np.linspace(0, 1, k)
    if r: e *= np.exp(-np.arange(n) / (SR * r))
    return e
def lowpass(x, cut):
    a = np.exp(-2 * np.pi * np.asarray(cut) / SR); y = np.zeros_like(x); p = 0.0
    a = np.broadcast_to(a, x.shape)
    for i in range(len(x)): p = (1 - a[i]) * x[i] + a[i] * p; y[i] = p
    return y
def sweep(f0, f1, d, shape='exp'):
    t = t_(d); f = f0 * (f1 / f0) ** (t / d) if shape == 'exp' else np.linspace(f0, f1, len(t))
    return np.sin(2 * np.pi * np.cumsum(f) / SR)
def add(at, x, g=1.0):
    i = int(at * SR); out[i:i + len(x)] += g * x[:len(out) - i]

def whoosh(d=0.35):
    n = int(SR * d); x = rng.standard_normal(n)
    cut = 300 + 5000 * np.sin(np.linspace(0, np.pi, n)) ** 2
    y = lowpass(x, cut) - lowpass(x, cut * 0.25)
    return y * np.sin(np.linspace(0, np.pi, n)) ** 1.5 * 1.6
def pop(f=700):
    d = 0.09; return sweep(f * 1.8, f * 0.6, d) * env(int(SR * d), 0.001, 0.025)
def blip(f): d = 0.12; return np.sin(2 * np.pi * f * t_(d)) * env(int(SR * d), 0.002, 0.04)
def ding(f=1318.5):
    d = 1.2; t = t_(d); y = sum(np.sin(2 * np.pi * f * h * t) / h ** 1.3 for h in (1, 2.01, 3.03))
    return y * env(len(t), 0.002, 0.28) * 0.6
def boom():
    d = 0.45; return (sweep(140, 45, d) * env(int(SR * d), 0.002, 0.12) + 0.3 * lowpass(rng.standard_normal(int(SR * d)), 900) * env(int(SR * d), 0.001, 0.03)) * 1.1
def tick(f=3200):
    d = 0.03; x = rng.standard_normal(int(SR * d)); return (x - lowpass(x, f)) * env(len(x), 0.0005, 0.006) * 1.2 + 0.4 * blip(f / 2)[:len(x)]
def slide(f0, f1, d): return sweep(f0, f1, d, 'lin') * env(int(SR * d), 0.01) * np.linspace(1, 0.3, int(SR * d)) * 0.45
def sparkle(n=7, d=0.06):
    y = np.zeros(int(SR * (n * d + 0.4)))
    for i in range(n):
        b = blip(2000 + 400 * (i % 4) + 150 * i) * 0.5; s = int(i * d * SR); y[s:s + len(b)] += b
    return y
def sting(): y = np.zeros(int(SR * 0.9)); w = whoosh(0.25); y[:len(w)] += w; b = boom(); y[int(.18*SR):int(.18*SR)+len(b)] += b; return y
def thunk(): d = 0.25; return (sweep(220, 80, d) * env(int(SR * d), 0.001, 0.05) + 0.6 * lowpass(rng.standard_normal(int(SR * d)), 2500) * env(int(SR * d), 0.0005, 0.012))
def shutter(): a = tick(2500) * 2; y = np.zeros(int(SR * .12)); y[:len(a)] += a; y[int(.06*SR):int(.06*SR)+len(a)] += a * .8; return y

# scene cuts
for at in [0, 2.86, 7.38, 18.82, 24.26, 27.98, 31.16, 39.88]: add(max(0, at - 0.12), whoosh(), 0.55)
for at in [11.28, 35.26]: add(at - 0.12, sting(), 0.7)
# 1 hook
add(0.05, pop(600), .6); add(0.15, pop(760), .6); add(0.25, boom(), .7); add(1.9, pop(900), .6)
# 2 clock ticks, then the big 6
for i, at in enumerate(np.arange(3.2, 5.8, 0.32)): add(at, tick(3200 if i % 2 else 2400), .5)
add(5.88, boom(), .8); add(5.88, ding(), .55); add(6.05, pop(820), .5)
# 3 normal magnesium falls off
add(7.5, pop(650), .5); add(8.8, pop(900), .6); add(10.0, slide(900, 220, .7), .6)
# 4 steady release
add(11.5, pop(760), .5); add(11.6, pop(620), .5); add(14.8, pop(900), .6); add(14.8, slide(300, 700, 1.6) * np.linspace(.2, 1, int(SR * 1.6)), .35)
add(17.5, boom(), .7); add(17.5, ding(1568), .5)
# 5 level stays high
add(19.0, pop(650), .5); add(19.85, pop(820), .5); add(20.4, slide(250, 900, .6), .5)
for i in range(6): add(21.0 + i * 0.4, blip(523.25 * 2 ** (i * 2 / 12)), .5)
add(22.5, boom(), .75); add(22.5, ding(1760), .5)
# 6 tiny but multi-coated
add(24.3, shutter(), .6)
for i in range(5): add(25.4 + i * 0.3, pop(500 + 120 * i), .6)
add(25.6, boom(), .6)
# 7 slow release
add(28.0, pop(700), .5); add(28.3, sparkle(), .55); add(29.2, pop(950), .5)
# 8 general purpose scatters
add(31.3, pop(600), .5); add(31.6, boom(), .6)
for i in range(8): add(31.95 + i * 0.12, pop(1100 - 40 * i), .35)
add(33.0, slide(500, 300, .3), .5)
# 9 one target
add(35.6, pop(650), .5); add(36.55, whoosh(.3), .6); add(36.88, thunk(), .9); add(36.9, boom(), .5); add(37.9, ding(1318.5), .5); add(37.9, pop(820), .5)
# 10 call to action
add(39.9, pop(650), .5); add(40.0, pop(780), .5); add(40.2, boom(), .7); add(41.0, ding(1568), .5); add(41.0, sparkle(9), .5); add(41.4, pop(900), .45)

out = out[:int(SR * DUR)]
out = out / max(1e-9, np.abs(out).max()) * 0.6
w = wave.open(sys.argv[1], 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((out * 32767).astype(np.int16).tobytes()); w.close()
