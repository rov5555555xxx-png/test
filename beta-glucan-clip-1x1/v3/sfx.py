# Synthesizes the (deliberately sparse) sound-effect track for the clip; cue times match the animation delays in index.html.
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
def typing(n=8, gap=0.06):
    y = np.zeros(int(SR * (n * gap + 0.1)))
    for i in range(n):
        k = tick(1800 + 300 * (i % 3)) * (0.8 + 0.4 * rng.random()); s0 = int(i * gap * SR); y[s0:s0 + len(k)] += k
    return y
def marker(d=0.4):
    n = int(SR * d); x = rng.standard_normal(n); y = lowpass(x, 3500) - lowpass(x, 900)
    return y * np.sin(np.linspace(0, np.pi, n)) * 1.8
def chime():
    y = np.zeros(int(SR * 2.2))
    for i, f in enumerate((1046.5, 1318.5, 1568, 2093)):
        d = ding(f) * 0.5; s0 = int(i * 0.12 * SR); y[s0:s0 + len(d)] += d
    return y
def shutter(): a = tick(2500) * 2; y = np.zeros(int(SR * .12)); y[:len(a)] += a; y[int(.06*SR):int(.06*SR)+len(a)] += a * .8; return y

# soft transitions only on the main scene changes
for at in [4.22, 9.34, 16.8, 23.42, 28.0, 31.0, 39.78, 47.5]: add(max(0, at - 0.12), whoosh(), 0.3)
for at in (0.0, 0.7, 1.4): add(at, shutter(), .45)
add(0.45, whoosh(.3), .25); add(2.05, whoosh(.25), .3); add(2.15, boom(), .5); add(2.4, pop(820), .3); add(2.7, sparkle(6), .18)
for at in [4.35, 6.3, 7.2, 8.2]: add(at, pop(700), .3)
add(9.7, boom(), .45); add(9.75, sparkle(), .25); add(11.5, pop(820), .3)
add(15.2, thunk(), .45); add(15.8, thunk(), .45)
add(17.4, thunk(), .35); add(17.0, boom(), .5); add(17.0, ding(1318.5), .3); add(17.95, pop(820), .3)
add(21.3, slide(300, 900, .6), .3)
add(23.5, thunk(), .55)
for at in [25.6, 26.2, 26.8, 27.4]: add(at, pop(760), .25)
add(28.45, ding(1568), .35); add(30.4, pop(820), .3)
add(35.3, boom(), .4)
for i, at in enumerate([35.8, 36.05, 36.3, 36.55]): add(at, blip(880 * 2 ** (i * 2 / 12)), .22)
add(37.9, blip(1046.5), .3); add(38.6, blip(1318.5), .3)
add(40.0, boom(), .5); add(41.9, pop(820), .3)
for i, at in enumerate([44.1, 44.9, 45.7, 46.5]): add(at, blip(523.25 * 2 ** (i * 4 / 12)), .3)
add(46.7, whoosh(.25), .3); add(46.95, ding(2093), .3)
add(47.9, boom(), .45); add(49.2, sparkle(6), .18); add(51.4, ding(1568), .4); add(51.4, sparkle(9), .3)

out = out[:int(SR * DUR)]
out = out / max(1e-9, np.abs(out).max()) * 0.6
w = wave.open(sys.argv[1], 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((out * 32767).astype(np.int16).tobytes()); w.close()
