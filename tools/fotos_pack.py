"""Prepara o pack de fotos reais (Unsplash/Pexels) para o guia.
estudio-*  -> recorte de fundo (rembg isnet) -> assets/img/foto/<nome>.webp (com transparência, 1600 px)
cor-*, cena-*, ambiente-* -> assets/img/foto/<nome>.webp (2000 px) e <nome>-900.webp"""
import sys, glob, os
from PIL import Image, ImageFilter
SRC = "/Volumes/hd caique becker/Mac Caique/Downloads/ourofino-fotos/"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets/img/foto/")
os.makedirs(OUT, exist_ok=True)

def reduz(im, m):
    if max(im.size) > m:
        f = m / max(im.size); im = im.resize((round(im.width * f), round(im.height * f)), Image.LANCZOS)
    return im

def recorta(arq):
    from rembg import new_session, remove
    global SESS
    if "SESS" not in globals(): SESS = new_session("isnet-general-use")
    nome = os.path.basename(arq)[:-4]
    im = reduz(Image.open(arq).convert("RGB"), 1800)
    r = remove(im, session=SESS, alpha_matting=True, alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=15, alpha_matting_erode_size=10)
    a = r.split()[3].filter(ImageFilter.GaussianBlur(0.5)); r.putalpha(a)
    bb = a.point(lambda v: 255 if v > 14 else 0).getbbox()
    if bb: r = r.crop(bb)
    reduz(r, 1600).save(OUT + nome + ".webp", quality=88, method=6)
    return nome, r.size

def converte(arq):
    nome = os.path.basename(arq)[:-4]
    im = Image.open(arq).convert("RGB")
    reduz(im, 2000).save(OUT + nome + ".webp", quality=84, method=6)
    reduz(im, 900).save(OUT + nome + "-900.webp", quality=80, method=6)
    return nome, im.size

if __name__ == "__main__":
    alvo = sys.argv[1:] or ["estudio", "cor", "cena", "ambiente"]
    for f in sorted(glob.glob(SRC + "*.jpg")):
        b = os.path.basename(f)
        if not any(b.startswith(a) for a in alvo): continue
        print(*(recorta(f) if b.startswith("estudio") else converte(f)), flush=True)
