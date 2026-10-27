# Box front from the marble photo: the matte is replaced by an exact, slightly inset quadrilateral
# (anti-aliased at 4x), so the edges are perfectly straight with no marble or side-face slivers.
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
cut = Image.open(sys.argv[1])
tl, tr, br, bl = (24 + 5, 18 + 7), (491 - 7, 19 + 7), (509 - 12, 755 - 5), (26 + 5, 765 - 5)
S = 4
m = Image.new('L', (cut.width * S, cut.height * S), 0)
ImageDraw.Draw(m).polygon([(x * S, y * S) for x, y in (tl, tr, br, bl)], fill=255)
m = m.filter(ImageFilter.GaussianBlur(S * .6)).resize(cut.size, Image.LANCZOS)
im = cut.convert('RGB')
im = ImageEnhance.Contrast(im).enhance(1.06); im = ImageEnhance.Color(im).enhance(1.05)
im = im.filter(ImageFilter.UnsharpMask(1.2, 50, 2))
im.putalpha(m); im = im.crop(im.getbbox()); im.save(sys.argv[2]); print(im.size)
bg = Image.new('RGBA', im.size, (0, 200, 255, 255)); bg.alpha_composite(im); bg.convert('RGB').save(sys.argv[2] + '.chk.jpg')
