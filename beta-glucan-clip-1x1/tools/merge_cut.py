# Final product cutout: original pixels, alpha = flood-fill key (solid, keeps pale panels)
# combined with the AI matte (clean soft edges); only the AI matte is trusted near the base,
# so the table edge never comes along.
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageChops, ImageFilter
src, box, ai_png, out, base_band = sys.argv[1], tuple(map(int, sys.argv[2].split(','))), sys.argv[3], sys.argv[4], int(sys.argv[5])
im = Image.open(src).convert('RGB').crop(box)
w = im.copy(); key = (255, 0, 255)
for x in range(0, w.width, 20):
    for y in (0, w.height - 1):
        if w.getpixel((x, y)) != key: ImageDraw.floodfill(w, (x, y), key, thresh=14)
for y in range(0, w.height, 20):
    for x in (0, w.width - 1):
        if w.getpixel((x, y)) != key: ImageDraw.floodfill(w, (x, y), key, thresh=14)
F = Image.fromarray(((np.array(ImageChops.difference(w, Image.new('RGB', w.size, key)).convert('L')) > 0) * 255).astype(np.uint8))
F = np.array(F.filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(1.3))).astype(float)
A = np.array(Image.open(ai_png).getchannel('A')).astype(float)
rows = np.nonzero(A.max(axis=1) > 200)[0]; base = rows.max()
F[base - base_band:, :] = 0                      # near the base: AI matte only
F = np.minimum(F, np.array(Image.fromarray(((A > 8) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(31))).astype(float))  # never far outside the AI silhouette
alpha = np.maximum(A, F)
im.putalpha(Image.fromarray(alpha.astype(np.uint8)))
im = im.crop(im.getbbox()); im.save(out)
bg = Image.new('RGBA', im.size, (0, 150, 0, 255)); bg.alpha_composite(im); bg.convert('RGB').save(out + '.chk.jpg')
print(out, im.size)
