import sys, os
os.environ["U2NET_HOME"] = sys.argv[1]
from rembg import remove, new_session
from PIL import Image
s = new_session("isnet-general-use")
for spec in sys.argv[2:]:
    src, box, out = spec.split("|")
    im = Image.open(src).convert("RGB").crop(tuple(map(int, box.split(","))))
    r = remove(im, session=s)
    a = r.getchannel("A"); im.putalpha(a)          # keep the original pixels, take only the matte
    im = im.crop(im.getbbox()); im.save(out)
    bg = Image.new("RGBA", im.size, (0, 150, 0, 255)); bg.alpha_composite(im); bg.convert("RGB").save(out + ".chk.jpg")
    print(out, im.size)
