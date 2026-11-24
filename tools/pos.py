"""Pós-produção dos renders (color grading): contraste, saturação, split toning, bloom, vinheta, nitidez.
Uso: python3 tools/pos.py SHOT [SHOT ...]   (lê assets/render/<SHOT>.png e grava assets/img/<shot>.webp e <shot>-900.webp)
     python3 tools/pos.py --todos"""
import glob, os, sys
import numpy as np
from PIL import Image, ImageFilter

SRC = "assets/render/"; DST = "assets/img/"; os.makedirs(DST, exist_ok=True)
MAXW = 2000

def grade(path, out):
    im = Image.open(path)
    a = np.asarray(im).astype(np.float32)
    a = a / (65535.0 if a.max() > 255 else 255.0)
    if a.shape[2] == 4: a = a[..., :3]
    lum = lambda x: x[..., 0] * 0.2126 + x[..., 1] * 0.7152 + x[..., 2] * 0.0722
    # contraste em S suave
    s = a * a * (3 - 2 * a); a = a * 0.62 + s * 0.38
    # saturação
    l = lum(a)[..., None]; a = l + (a - l) * 1.14
    # split toning: sombras levemente frias, luzes levemente quentes
    l = lum(a)[..., None]
    a = a + (1 - l) ** 2 * np.array([-0.012, 0.0, 0.016]) + l ** 2 * np.array([0.018, 0.008, -0.012])
    a = np.clip(a, 0, 1)
    # bloom nas altas luzes
    h, w = a.shape[:2]
    hi = np.clip((lum(a) - 0.82) / 0.18, 0, 1)[..., None] * a
    hi_im = Image.fromarray((hi * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(radius=max(6, w * 0.012)))
    a = np.clip(a + np.asarray(hi_im).astype(np.float32) / 255 * 0.22, 0, 1)
    # vinheta
    yy, xx = np.mgrid[0:h, 0:w]; r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2) / 1.414
    a = a * (1 - 0.20 * np.clip(r, 0, 1) ** 2.2)[..., None]
    out_im = Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8))
    out_im = out_im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=55, threshold=2))
    tam = []
    for larg, suf, q in ((1800, "", 84), (900, "-900", 80)):
        im2 = out_im.resize((larg, round(out_im.height * larg / out_im.width)), Image.LANCZOS) if out_im.width > larg else out_im
        im2.save(out + suf + ".webp", quality=q, method=6); tam.append(im2.size)
    return tam

shots = [os.path.basename(f)[:-4] for f in sorted(glob.glob(SRC + "[FO]-*.png"))] if "--todos" in sys.argv else sys.argv[1:]
for s in shots:
    print(s, grade(SRC + s + ".png", DST + s.lower()))
