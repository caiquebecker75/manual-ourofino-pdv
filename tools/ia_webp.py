"""Converte as fotos e cenas do ChatGPT (assets/ia/loja-*.png e cena-*.png) em WebP para o site (tamanho nativo e 900 px).
Pets e personagem passam por tools/recorte.py (recorte de fundo).
Uso: python3 tools/ia_webp.py [nome ...]"""
import sys
from pathlib import Path
from PIL import Image

RAIZ = Path(__file__).resolve().parents[1]
IA = RAIZ / "assets/ia"; OUT = RAIZ / "assets/img"

def converter(nome):
    im = Image.open(IA / f"{nome}.png").convert("RGB")
    im.save(OUT / f"{nome}.webp", quality=86, method=6)
    if im.width > 900:
        im.resize((900, round(im.height * 900 / im.width)), Image.LANCZOS).save(OUT / f"{nome}-900.webp", quality=82, method=6)
    else:
        im.save(OUT / f"{nome}-900.webp", quality=82, method=6)
    return im.size

if __name__ == "__main__":
    nomes = sys.argv[1:] or sorted(p.stem for p in IA.glob("*.png") if p.stem.startswith(("loja-", "cena-")))
    for n in nomes: print(n, converter(n), flush=True)
