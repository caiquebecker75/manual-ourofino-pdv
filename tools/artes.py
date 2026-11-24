"""Gera as artes impressas (texturas) dos materiais de PDV, embalagens genéricas e etiquetas de preço.
Rodar da raiz do repo: python3 tools/artes.py  ->  assets/tex/arte_*.png, gen_*.png, preco_*.png"""
import os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

T = "assets/tex/"
F = os.path.expanduser("~/Library/Fonts/")
def font(w, s): return ImageFont.truetype(F + f"Lexend-{w}.ttf", s)

NAVY = (7, 32, 71); GREEN = (16, 173, 49); BLUE = (0, 124, 193); CYAN = (32, 213, 242)
WHITE = (255, 255, 255); CREAM = (247, 244, 236)

def pack(sku, h):
    """embalagem real (frente endireitada ou recorte) redimensionada para altura h"""
    p = T + (f"{sku}_front.png" if os.path.exists(T + f"{sku}_front.png") else f"{sku}_bb.png")
    im = Image.open(p).convert("RGBA"); k = h / im.height
    return im.resize((max(1, round(im.width * k)), h), Image.LANCZOS)

def shadow_paste(base, im, xy, blur=18, off=(0, 14), alpha=110):
    sh = Image.new("RGBA", (im.width + blur * 4, im.height + blur * 4), (0, 0, 0, 0))
    a = im.getchannel("A").point(lambda v: alpha if v > 10 else 0)
    sh.paste((0, 0, 0, 255), (blur * 2, blur * 2), a)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(sh, (xy[0] - blur * 2 + off[0], xy[1] - blur * 2 + off[1]))
    base.alpha_composite(im, xy)

# logo oficial (site de identidade visual Ourofino), versão sem slogan
def logo(h, escuro=False):
    f = "assets/marca/" + ("ourofino_fundo_escuro_semslogan.png" if escuro else "ourofino_positivo_semslogan.png")
    lg = Image.open(f).convert("RGBA"); k = h / lg.height
    return lg.resize((round(lg.width * k), h), Image.LANCZOS)

def logo_pill(h, pad=0.45):
    lg = logo(h)
    pw, ph = lg.width + int(h * pad * 2), int(h * (1 + pad))
    pill = Image.new("RGBA", (pw, ph), (0, 0, 0, 0)); d = ImageDraw.Draw(pill)
    d.rounded_rectangle((0, 0, pw - 1, ph - 1), radius=ph // 2, fill=WHITE)
    pill.alpha_composite(lg, ((pw - lg.width) // 2, (ph - h) // 2)); return pill

def ctext(d, cx, y, txt, f, fill):
    w = d.textlength(txt, font=f); d.text((cx - w / 2, y), txt, font=f, fill=fill)

out = {}

# 1. WOBBLER (disco) · WellPET
im = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
d.ellipse((0, 0, 1023, 1023), fill=NAVY); d.ellipse((28, 28, 995, 995), outline=GREEN, width=22)
shadow_paste(im, pack("wellpet_d", 520), (300, 150))
ctext(d, 512, 690, "WellPET", font("Black", 108), WHITE)
ctext(d, 512, 815, "pulga e carrapato", font("Medium", 52), (190, 230, 200))
im.save(T + "arte_wobbler.png"); out["wobbler"] = im.size

# 2. STOPPER (placa vertical) · EnziClim (higiene do ambiente)
im = Image.new("RGBA", (800, 1200), (18, 128, 84, 255)); d = ImageDraw.Draw(im)
d.rectangle((0, 0, 799, 70), fill=NAVY)
ctext(d, 400, 14, "higiene do ambiente", font("Bold", 38), WHITE)
ctext(d, 400, 140, "EnziClim", font("Black", 132), WHITE)
ctext(d, 400, 310, "contra odor e mancha", font("Medium", 52), (205, 245, 222))
shadow_paste(im, pack("enziclim", 600), (300, 400))
pl = logo_pill(70); im.alpha_composite(pl, ((800 - pl.width) // 2, 1070))
im.save(T + "arte_stopper.png"); out["stopper"] = im.size

# 3. TESTEIRA (cabeceira da gôndola, 2 m x 0,30 m)
im = Image.new("RGBA", (2400, 360), NAVY + (255,)); d = ImageDraw.Draw(im)
d.rectangle((0, 300, 2399, 359), fill=GREEN)
f1 = font("Black", 100); d.text((90, 92), "Saúde e proteção", font=f1, fill=WHITE)
x2 = 90 + d.textlength("Saúde e proteção", font=f1) + 34
d.text((x2, 116), "para o seu pet", font=font("Medium", 72), fill=(170, 230, 190))
pl = logo_pill(110); im.alpha_composite(pl, (2400 - pl.width - 80, (300 - pl.height) // 2))
im.save(T + "arte_testeira.png"); out["testeira"] = im.size

# 4. RÉGUA de gôndola (faixa do preço, 1 m x 0,04 m)
im = Image.new("RGBA", (2500, 100), GREEN + (255,)); d = ImageDraw.Draw(im)
x = 40; fr = font("Bold", 46); tw = d.textlength("Proteção e prevenção", font=fr)
while x < 2500:
    d.text((x, 22), "Proteção e prevenção", font=fr, fill=WHITE)
    d.ellipse((x + tw + 36, 40, x + tw + 58, 62), fill=(200, 245, 210)); x += tw + 96
im.save(T + "arte_regua.png"); out["regua"] = im.size

# 5. DISPLAY DE BALCÃO (cabeçalho) · Top Dog
im = Image.new("RGBA", (1000, 560), (201, 70, 88, 255)); d = ImageDraw.Draw(im)
d.text((60, 50), "Top Dog", font=font("Black", 140), fill=WHITE)
d.text((66, 225), "vermífugo palatável", font=font("Medium", 50), fill=(255, 225, 230))
d.text((66, 290), "para cães", font=font("Medium", 50), fill=(255, 225, 230))
shadow_paste(im, pack("topdog_b", 190), (620, 340))
pl = logo_pill(52); im.alpha_composite(pl, (60, 440))
im.save(T + "arte_balcao.png"); out["balcao"] = im.size

# 6. TAKE ONE (folheto)
im = Image.new("RGBA", (600, 850), CREAM + (255,)); d = ImageDraw.Draw(im)
d.rectangle((0, 0, 599, 330), fill=NAVY)
d.text((44, 60), "Calendário", font=font("Black", 78), fill=WHITE)
d.text((44, 150), "de vermifugação", font=font("Medium", 58), fill=(170, 230, 190))
d.text((44, 238), "do seu cão", font=font("Medium", 58), fill=(170, 230, 190))
for i in range(6):
    y = 380 + i * 62; d.rounded_rectangle((44, y, 556, y + 44), radius=10, outline=(200, 205, 195), width=3)
    d.text((64, y + 6), ["jan", "mar", "mai", "jul", "set", "nov"][i], font=font("Bold", 30), fill=NAVY)
pl = logo_pill(52); im.alpha_composite(pl, ((600 - pl.width) // 2, 760))
im.save(T + "arte_takeone.png"); out["takeone"] = im.size

# 7. DISPLAY DE CHÃO (cabeçalho e lateral) · Herbalvet T.A.
im = Image.new("RGBA", (900, 700), (14, 120, 52, 255)); d = ImageDraw.Draw(im)
d.rectangle((0, 610, 899, 699), fill=NAVY)
d.text((60, 50), "Herbalvet T.A.", font=font("Black", 112), fill=WHITE)
d.text((66, 205), "desinfetante para", font=font("Medium", 50), fill=(205, 245, 222))
d.text((66, 268), "pisos e canis", font=font("Medium", 50), fill=(205, 245, 222))
shadow_paste(im, pack("herbalvet", 330), (560, 260))
pl = logo_pill(52); im.alpha_composite(pl, (60, 500))
im.save(T + "arte_displaychao.png"); out["displaychao"] = im.size
lat = Image.new("RGBA", (400, 1400), (14, 120, 52, 255)); d = ImageDraw.Draw(lat)
d.rectangle((0, 1300, 399, 1399), fill=NAVY)
lat.save(T + "arte_displaychao_lat.png")

# 8. ILHA (face do cubo) · higiene do ambiente
im = Image.new("RGBA", (800, 800), (14, 120, 52, 255)); d = ImageDraw.Draw(im)
d.text((50, 50), "Ambiente", font=font("Black", 104), fill=WHITE)
d.text((54, 170), "limpo e sem odor", font=font("Medium", 54), fill=(200, 245, 210))
shadow_paste(im, pack("herbalvet", 420), (70, 290)); shadow_paste(im, pack("enziclim", 400), (470, 310))
im.save(T + "arte_ilha.png"); out["ilha"] = im.size

# 9. CLIP STRIP (cabeçalho) · Banni 3
im = Image.new("RGBA", (400, 300), (110, 150, 120, 255)); d = ImageDraw.Draw(im)
ctext(d, 200, 40, "Banni 3", font("Black", 86), WHITE)
ctext(d, 200, 150, "para gatos", font("Medium", 44), (230, 245, 232))
im.save(T + "arte_clipstrip.png"); out["clipstrip"] = im.size

# 10. CARTAZ (A1)
im = Image.new("RGBA", (1188, 1682), CREAM + (255,)); d = ImageDraw.Draw(im)
d.rectangle((0, 0, 1187, 760), fill=NAVY)
d.text((90, 110), "Seu pet", font=font("Black", 170), fill=WHITE)
d.text((90, 300), "protegido", font=font("Black", 170), fill=GREEN)
d.text((96, 520), "o ano todo", font=font("Medium", 96), fill=(170, 230, 190))
shadow_paste(im, pack("wellpet_c", 520), (120, 860)); shadow_paste(im, pack("leevre_b", 470), (440, 900))
shadow_paste(im, pack("topdog_c", 260), (700, 1130))
pl = logo_pill(90); im.alpha_composite(pl, ((1188 - pl.width) // 2, 1520))
im.save(T + "arte_cartaz.png"); out["cartaz"] = im.size

# 11. ADESIVO DE CHÃO (círculo com seta)
im = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
d.ellipse((0, 0, 1023, 1023), fill=GREEN); d.ellipse((40, 40, 983, 983), outline=WHITE, width=12)
d.polygon([(512, 120), (690, 330), (580, 330), (580, 470), (444, 470), (444, 330), (334, 330)], fill=WHITE)
ctext(d, 512, 540, "Proteção contra", font("Bold", 74), WHITE)
ctext(d, 512, 630, "pulga e carrapato", font("Bold", 74), WHITE)
ctext(d, 512, 760, "na farmácia", font("Medium", 58), (210, 248, 220))
im.save(T + "arte_adesivo.png"); out["adesivo"] = im.size

# 12. CUBO WellPET (usado na ilha errada, o "carnaval")
im = Image.new("RGBA", (800, 800), NAVY + (255,)); d = ImageDraw.Draw(im)
d.text((60, 60), "WellPET", font=font("Black", 130), fill=WHITE)
d.text((66, 220), "pulga e carrapato", font=font("Medium", 56), fill=(170, 230, 190))
shadow_paste(im, pack("wellpet_b", 400), (300, 330))
im.save(T + "arte_cubo_wellpet.png"); out["cubo_wellpet"] = im.size

# 13. EMBALAGENS GENÉRICAS (concorrentes e outras categorias, sem marca)
random.seed(7)
GEN = {"gen_laranja": (232, 120, 36), "gen_azul": (52, 92, 150), "gen_roxo": (98, 62, 140), "gen_amarelo": (236, 196, 40),
       "gen_petroleo": (22, 110, 118), "gen_vinho": (128, 34, 52), "gen_cinza": (96, 104, 116), "gen_verdeagua": (70, 170, 150)}
for name, col in GEN.items():
    im = Image.new("RGB", (600, 800), col); d = ImageDraw.Draw(im)
    lt = tuple(min(255, c + 70) for c in col)
    d.rounded_rectangle((40, 60, 400, 150), radius=24, fill=WHITE)
    d.rounded_rectangle((70, 85, 300, 125), radius=10, fill=lt)
    for i in range(3): d.rounded_rectangle((44, 190 + i * 44, 44 + random.randint(260, 470), 214 + i * 44), radius=8, fill=lt)
    d.ellipse((310, 380, 560, 630), fill=lt); d.ellipse((350, 420, 520, 590), fill=col)
    d.rectangle((0, 700, 599, 799), fill=WHITE)
    d.rounded_rectangle((40, 725, 260, 775), radius=12, fill=col)
    im.save(T + f"{name}.png")
# pote de suplemento genérico (rótulo de cilindro)
for name, col in {"pote_azul": (40, 110, 180), "pote_laranja": (230, 110, 40), "pote_verde": (60, 150, 90)}.items():
    im = Image.new("RGB", (1200, 500), WHITE); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 1199, 120), fill=col); d.rectangle((0, 420, 1199, 499), fill=col)
    for k in range(2):
        x0 = 120 + k * 600; d.rounded_rectangle((x0, 170, x0 + 330, 230), radius=14, fill=col)
        d.rounded_rectangle((x0, 260, x0 + 260, 290), radius=8, fill=(205, 210, 215))
        d.rounded_rectangle((x0, 310, x0 + 200, 340), radius=8, fill=(205, 210, 215))
    im.save(T + f"{name}.png")
# saco de ração genérico
for name, col in {"racao_vermelha": (180, 40, 40), "racao_azul": (30, 70, 140), "racao_verde": (40, 120, 60), "racao_mostarda": (200, 150, 30)}.items():
    im = Image.new("RGB", (700, 1000), col); d = ImageDraw.Draw(im)
    lt = tuple(min(255, c + 80) for c in col)
    d.rounded_rectangle((60, 70, 640, 230), radius=30, fill=WHITE)
    d.rounded_rectangle((110, 115, 520, 185), radius=14, fill=lt)
    d.ellipse((150, 380, 550, 780), fill=lt)
    d.polygon([(300, 470), (420, 470), (470, 600), (360, 700), (250, 600)], fill=col)
    d.rectangle((0, 880, 699, 999), fill=WHITE)
    im.save(T + f"{name}.png")

# 14. ETIQUETAS DE PREÇO
precos = ["89,90", "64,50", "119,90", "42,90", "152,00", "37,90", "74,90", "58,40"]
for i, p in enumerate(precos):
    im = Image.new("RGB", (360, 160), (255, 236, 80)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 359, 34), fill=WHITE)
    d.rounded_rectangle((14, 8, 200, 24), radius=6, fill=(200, 200, 200))
    d.text((24, 50), "R$", font=font("Bold", 40), fill=(20, 20, 20))
    d.text((90, 38), p, font=font("Black", 92), fill=(20, 20, 20))
    im.save(T + f"preco_{i}.png")

# 15. CHAPA PERFURADA (fundo da gôndola)
im = Image.new("RGB", (512, 512), (214, 217, 220)); d = ImageDraw.Draw(im)
for gx in range(16):
    for gy in range(16):
        cx, cy = 16 + gx * 32, 16 + gy * 32; d.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=(120, 124, 130))
im.save(T + "chapa.png")
print(out)
