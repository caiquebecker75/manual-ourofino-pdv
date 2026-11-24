"""Endireita a face frontal das embalagens (fotos em 3/4) para usar como textura no Blender.
Uso: python3 tools/warp_fronts.py   (roda a partir da raiz do repo)
Saída: assets/tex/<sku>_front.png + assets/tex/caixas.json (dimensões e cores laterais)."""
import json, os
import numpy as np
from PIL import Image

RAW = "assets/produtos/raw"
OUT = "assets/tex"
os.makedirs(OUT, exist_ok=True)

# quads no espaço da imagem escalada para 1000 px no maior lado: TL, TR, BR, BL
Q = {
    "topdog": [(240, 222), (868, 152), (868, 525), (240, 582)],
    "banni3": [(250, 128), (728, 100), (742, 722), (250, 752)],
    "leevre": [(240, 78), (748, 62), (748, 640), (240, 652)],
    "wellpet": [(440, 197), (655, 183), (655, 718), (440, 748)],
}
# dimensões reais aproximadas em metros (largura, profundidade, altura) e ponto de amostra da lateral
SKUS = {
    "topdog_a": ("topdog", (0.125, 0.022, 0.072), (210, 400)),
    "topdog_b": ("topdog", (0.125, 0.022, 0.072), (210, 400)),
    "topdog_c": ("topdog", (0.140, 0.026, 0.080), (210, 400)),
    "banni3_a": ("banni3", (0.090, 0.022, 0.115), (236, 520)),
    "banni3_b": ("banni3", (0.090, 0.022, 0.115), (236, 520)),
    "leevre_a": ("leevre", (0.140, 0.040, 0.160), (765, 330)),
    "leevre_b": ("leevre", (0.150, 0.040, 0.170), (765, 330)),
    "wellpet_a": ("wellpet", (0.060, 0.030, 0.150), (410, 420)),
    "wellpet_b": ("wellpet", (0.060, 0.030, 0.150), (410, 420)),
    "wellpet_c": ("wellpet", (0.060, 0.030, 0.150), (410, 420)),
    "wellpet_d": ("wellpet", (0.060, 0.030, 0.150), (410, 420)),
    "wellpet_e": ("wellpet", (0.060, 0.030, 0.150), (410, 420)),
}

def coeffs(dst, src):
    """coeficientes de Image.transform PERSPECTIVE: mapeia ponto de saída (dst) -> entrada (src)."""
    A, B = [], []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); B.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); B.append(v)
    return np.linalg.solve(np.array(A, float), np.array(B, float)).tolist()

meta = {}
for sku, (fam, dims, side_pt) in SKUS.items():
    im = Image.open(f"{RAW}/{sku}.png").convert("RGBA")
    k = 1000 / max(im.size)
    im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    flat = Image.new("RGBA", im.size, (255, 255, 255, 255)); flat.alpha_composite(im); flat = flat.convert("RGB")
    w_m, d_m, h_m = dims
    H = 1024; W = max(64, round(H * w_m / h_m))
    c = coeffs([(0, 0), (W, 0), (W, H), (0, H)], Q[fam])
    front = flat.transform((W, H), Image.PERSPECTIVE, c, Image.BICUBIC)
    front.save(f"{OUT}/{sku}_front.png")
    side = flat.getpixel(side_pt)
    meta[sku] = {"dims": dims, "side": [round(v / 255, 4) for v in side], "front": f"{OUT}/{sku}_front.png"}
    print(sku, (W, H), "lateral", side)

json.dump(meta, open(f"{OUT}/caixas.json", "w"), indent=1)
