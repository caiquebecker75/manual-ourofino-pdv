"""Recorta o fundo branco das fotos de pets e da personagem (assets/ia/*.png) e grava WebP com transparência em assets/img/.
Uso: python3 tools/recorte.py [nome ...]   (padrão: todos os pet-* e bia-*)"""
import sys
from pathlib import Path
from PIL import Image, ImageFilter
from rembg import new_session, remove

RAIZ = Path(__file__).resolve().parents[1]
IA = RAIZ / "assets/ia"; OUT = RAIZ / "assets/img"
SESS = new_session("isnet-general-use")


def recortar(nome, maxl=1400):
    im = Image.open(IA / f"{nome}.png").convert("RGB")
    try:
        r = remove(im, session=SESS, alpha_matting=True, alpha_matting_foreground_threshold=245,
                   alpha_matting_background_threshold=18, alpha_matting_erode_size=8)
    except Exception:
        r = remove(im, session=SESS)
    a = r.split()[3]
    # tira o "halo" branco: suaviza a borda e escurece levemente os pixels semitransparentes
    a = a.filter(ImageFilter.GaussianBlur(0.6))
    r.putalpha(a)
    bb = a.point(lambda v: 255 if v > 12 else 0).getbbox()
    if bb:
        m = 12; r = r.crop((max(0, bb[0] - m), max(0, bb[1] - m), min(r.width, bb[2] + m), min(r.height, bb[3] + m)))
    if max(r.size) > maxl:
        f = maxl / max(r.size); r = r.resize((round(r.width * f), round(r.height * f)), Image.LANCZOS)
    r.save(OUT / f"{nome}.webp", quality=88, method=6)
    return r.size


if __name__ == "__main__":
    nomes = sys.argv[1:] or sorted(p.stem for p in IA.glob("*.png") if p.stem.startswith(("pet-", "bia-")))
    for n in nomes: print(n, recortar(n), flush=True)
