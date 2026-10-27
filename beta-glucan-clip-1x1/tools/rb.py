import sys, os
os.environ["U2NET_HOME"] = sys.argv[1]
from rembg import remove, new_session
from PIL import Image
s = new_session("isnet-general-use")
for src, box, out in [(sys.argv[2], (20, 20, 1065, 786), sys.argv[3]), (sys.argv[4], (262, 0, 1043, 890), sys.argv[5])]:
    im = Image.open(src).convert("RGB").crop(box)
    r = remove(im, session=s, alpha_matting=True, alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=15, alpha_matting_erode_size=8)
    r.save(out)
    bg = Image.new("RGBA", r.size, (0, 150, 0, 255)); bg.alpha_composite(r); bg.convert("RGB").save(out + ".chk.jpg")
    print(out, r.size, r.getbbox())
