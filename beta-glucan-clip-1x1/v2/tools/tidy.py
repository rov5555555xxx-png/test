# Tidies the two hero cutouts: the bottle is rebuilt as a mirror-symmetric silhouette from its
# clean left edge (removes the finger spike and the light strip on the right); the box loses the
# dark sliver of the neighbouring bottle along its left edge.
import sys
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

def sub_edge(row, thr=128):
    """Sub-pixel position of the first left-to-right crossing of thr, or None."""
    idx = np.nonzero(row > thr)[0]
    if not len(idx): return None
    x = idx[0]
    if x == 0: return 0.0
    a, b = row[x - 1], row[x]
    return x - 1 + (thr - a) / max(1e-6, b - a)

def bottle(src, out):
    im = Image.open(src); A = np.array(im.getchannel('A')).astype(float)
    H, W = A.shape
    L = np.array([sub_edge(A[y]) if A[y].max() > 128 else np.nan for y in range(H)], float)
    R = np.array([(W - 1 - sub_edge(A[y, ::-1])) if A[y].max() > 128 else np.nan for y in range(H)], float)
    band = slice(int(H * .45), int(H * .85))        # label rows: both edges are clean there
    c = np.nanmedian((L[band] + R[band]) / 2)
    xs = np.arange(W)[None, :]
    Rm = 2 * c - L                                     # mirrored right edge
    m = np.clip(xs - L[:, None] + .5, 0, 1) * np.clip(Rm[:, None] - xs + .5, 0, 1)
    m[np.isnan(L)] = 0
    solid = ndimage.binary_fill_holes(A > 128)
    keep = np.where(solid, 255.0, A) * m                # inside: fully opaque, edges: mirrored AA
    im.putalpha(Image.fromarray(np.clip(keep, 0, 255).astype(np.uint8)))
    im = im.crop(im.getbbox()); im.save(out); print('bottle centre', round(c, 1), im.size)

def box(src, out):
    im = Image.open(src); A = np.array(im.getchannel('A')).astype(float)
    H, W = A.shape
    # true left edge of the box runs from x≈19 at the top to x≈31 at the bottom
    ys = np.arange(H)[:, None]; xs = np.arange(W)[None, :]
    edge = 19 + (31 - 19) * ys / H
    m = np.clip(xs - edge + .5, 0, 1)
    solid = ndimage.binary_fill_holes(A > 100)
    A2 = np.where(solid, 255.0, A) * m
    A2 = np.array(Image.fromarray(A2.astype(np.uint8)).filter(ImageFilter.GaussianBlur(.5))).astype(float)
    im.putalpha(Image.fromarray(A2.astype(np.uint8)))
    im = im.crop(im.getbbox()); im.save(out); print('box', im.size)

bottle(sys.argv[1], sys.argv[2]); box(sys.argv[3], sys.argv[4])

def drop_skin(path, y0, y1, x0):
    """Clears skin-toned pixels (finger remnant) from a region of the bottle's neck."""
    im = Image.open(path); a = np.array(im).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    skin = (r > g + 15) & (r > b + 15)
    reg = np.zeros(skin.shape, bool); reg[y0:y1, x0:] = True
    A = a[..., 3].astype(float); A[skin & reg] = 0
    sm = np.array(Image.fromarray(A.astype(np.uint8)).filter(ImageFilter.MedianFilter(5))).astype(float)
    A[y0 - 4:y1 + 4, x0:] = sm[y0 - 4:y1 + 4, x0:]
    im.putalpha(Image.fromarray(A.astype(np.uint8))); im.save(path)

def heal_neck(path, ref, y0, y1, x0):
    """Fills the notch left by the finger with inpainted bottle texture, inside the mirrored silhouette
    taken from `ref` (the alpha straight after the mirror step), and recolours pink cap reflections."""
    import cv2
    im = np.array(Image.open(path)).astype(np.uint8)
    target = np.array(Image.open(ref).getchannel('A')) > 128
    A = im[..., 3]; rgb = im[..., :3].copy()
    r, g, b = [rgb[..., i].astype(int) for i in range(3)]
    reg = np.zeros(A.shape, bool); reg[y0:y1, x0:] = True
    hole = reg & target & (A < 200)
    pink = reg & (A > 0) & (r > g + 10) & (r > b + 10)
    mask = ndimage.binary_dilation(hole | pink, iterations=2) & target
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    fixed = cv2.cvtColor(cv2.inpaint(bgr, mask.astype(np.uint8) * 255, 6, cv2.INPAINT_TELEA), cv2.COLOR_BGR2RGB)
    rgb[mask] = fixed[mask]
    A2 = A.astype(float); A2[reg & target] = np.maximum(A2[reg & target], 255)
    edge = np.array(Image.fromarray(target.astype(np.uint8) * 255).filter(ImageFilter.GaussianBlur(.6))).astype(float)
    A2[reg] = np.minimum(A2[reg], edge[reg])
    out = np.dstack([rgb, A2.astype(np.uint8)]); Image.fromarray(out, 'RGBA').save(path)
    print('healed px', int(mask.sum()))

def mirror_heal(path, ref, y0, y1, x0):
    """Replaces finger-covered pixels on the right of the neck with the mirrored pixels from the
    clean left side of the same row (the bottle is symmetric), inside the mirrored silhouette."""
    src = np.array(Image.open(ref)).astype(np.uint8)
    A = src[..., 3].astype(float); H, W = A.shape
    L = np.array([sub_edge(A[y]) if A[y].max() > 128 else np.nan for y in range(H)])
    R = np.array([(W - 1 - sub_edge(A[y, ::-1])) if A[y].max() > 128 else np.nan for y in range(H)])
    c = np.nanmedian(((L + R) / 2)[int(H * .45):int(H * .85)])
    rgb = src[..., :3].copy()
    r, g, b = [rgb[..., i].astype(int) for i in range(3)]
    skin = (r > g + 8) & (r > b + 8)
    for y in range(y0, y1):
        for x in range(x0, W):
            if A[y, x] > 0 and (skin[y, x] or A[y, x] < 250):
                xm = int(round(2 * c - x))
                if 0 <= xm < W and A[y, xm] > 200:
                    rgb[y, x] = src[y, xm, :3]
                    A[y, x] = max(A[y, x], 255 if A[y, xm] > 250 else A[y, xm])
    Image.fromarray(np.dstack([rgb, A.astype(np.uint8)]), 'RGBA').save(path)
    print('centre', round(c, 1))

def clamp_cap(path, y0, y1, ref_rows):
    """Straightens the right edge under the cap to the cap's own right edge."""
    im = np.array(Image.open(path)).astype(float); A = im[..., 3]; W = A.shape[1]
    capR = np.median([W - 1 - sub_edge(A[y, ::-1]) for y in range(*ref_rows)])
    xs = np.arange(W)
    for y in range(y0, y1):
        A[y] = np.minimum(A[y], np.clip(capR - xs + .5, 0, 1) * 255)
    im[..., 3] = A; Image.fromarray(im.astype(np.uint8), 'RGBA').save(path); print('cap edge', round(capR, 1))
