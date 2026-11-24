"""Embalagens genéricas (concorrentes e outras categorias), em português e SEM marca.
Rodar da raiz: python3 tools/artes_genericos.py -> assets/tex/g2_*.png"""
import os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

T = "assets/tex/"; F = os.path.expanduser("~/Library/Fonts/")
def fnt(w, s): return ImageFont.truetype(F + f"Lexend-{w}.ttf", s)
WHITE = (255, 255, 255)

def fit(d, txt, peso, tam, maxw):
    while tam > 10 and d.textlength(txt, font=fnt(peso, tam)) > maxw: tam -= 2
    return fnt(peso, tam)

def grad(w, h, c1, c2, vertical=True):
    im = Image.new("RGB", (w, h), c1); px = im.load()
    for y in range(h):
        for x in range(0, w, 1):
            t = (y / h) if vertical else (x / w)
            px[x, y] = tuple(int(c1[i] * (1 - t) + c2[i] * t) for i in range(3))
    return im

def pata(d, cx, cy, r, col):
    d.ellipse((cx - r, cy - r * 0.55, cx + r, cy + r * 1.05), fill=col)
    for dx, dy in ((-1.05, -1.25), (-0.38, -1.75), (0.38, -1.75), (1.05, -1.25)):
        d.ellipse((cx + dx * r - r * 0.36, cy + dy * r - r * 0.42, cx + dx * r + r * 0.36, cy + dy * r + r * 0.42), fill=col)

def gota(d, cx, cy, r, col):
    d.ellipse((cx - r, cy - r * 0.2, cx + r, cy + r * 1.8), fill=col)
    d.polygon([(cx, cy - r * 1.6), (cx - r * 0.93, cy + r * 0.5), (cx + r * 0.93, cy + r * 0.5)], fill=col)

def caixa(nome, w, h, c1, c2, linha1, linha2, selo, icone="pata", tom_txt=WHITE):
    im = grad(w, h, c1, c2); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, int(h * 0.10)), fill=tuple(max(0, c - 40) for c in c1))
    d.text((int(w * .06), int(h * .025)), "USO VETERINÁRIO", font=fnt("Medium", int(h * .045)), fill=(235, 235, 235))
    f1 = fit(d, linha1, "Bold", int(h * .13), w * .88); s1 = f1.size
    d.text((int(w * .06), int(h * .17)), linha1, font=f1, fill=tom_txt)
    d.text((int(w * .065), int(h * .17) + s1 + int(h * .03)), linha2, font=fit(d, linha2, "Medium", int(h * .06), w * .88), fill=tom_txt)
    claro = tuple(min(255, c + 70) for c in c2)
    if icone == "pata": pata(d, int(w * .72), int(h * .66), int(h * .085), claro)
    else: gota(d, int(w * .72), int(h * .60), int(h * .08), claro)
    fs = fit(d, selo, "Bold", int(h * .055), w * .5)
    d.rounded_rectangle((int(w * .06), int(h * .80), int(w * .06 + d.textlength(selo, font=fs) + w * .07), int(h * .92)), radius=int(h * .03), fill=WHITE)
    d.text((int(w * .095), int(h * .815)), selo, font=fs, fill=c1)
    im.save(T + f"g2_{nome}.png")

def rotulo_cilindro(nome, c, linha1, linha2, w=1600, h=600, icone="pata"):
    im = Image.new("RGB", (w, h), (246, 246, 244)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, int(h * .16)), fill=c); d.rectangle((0, int(h * .86), w, h), fill=c)
    for k in (0, 1):  # dois painéis, frente e verso
        x0 = int(w * (0.10 + k * 0.5))
        d.text((x0, int(h * .24)), linha1, font=fnt("Bold", int(h * .14)), fill=c)
        d.text((x0, int(h * .44)), linha2, font=fnt("Medium", int(h * .075)), fill=(70, 74, 80))
        if icone == "pata": pata(d, x0 + int(w * .36), int(h * .74), int(h * .06), tuple(min(255, v + 90) for v in c))
        else: gota(d, x0 + int(w * .36), int(h * .70), int(h * .06), tuple(min(255, v + 90) for v in c))
    im.save(T + f"g2_{nome}.png")

def saco(nome, c1, c2, linha1, linha2, peso, w=900, h=1300, icone="pata"):
    im = grad(w, h, c1, c2); d = ImageDraw.Draw(im)
    d.rounded_rectangle((int(w * .07), int(h * .06), int(w * .93), int(h * .26)), radius=40, fill=WHITE)
    d.text((int(w * .12), int(h * .095)), linha1, font=fit(d, linha1, "Black", int(h * .062), w * .76), fill=c1)
    d.text((int(w * .12), int(h * .175)), linha2, font=fit(d, linha2, "Medium", int(h * .04), w * .76), fill=(60, 64, 70))
    claro = tuple(min(255, c + 80) for c in c2)
    d.ellipse((int(w * .18), int(h * .36), int(w * .82), int(h * .78)), fill=claro)
    if icone == "pata": pata(d, int(w * .5), int(h * .60), int(h * .09), c1)
    else:
        for k in range(9):
            rx, ry = random.randint(int(w * .3), int(w * .7)), random.randint(int(h * .45), int(h * .7))
            d.ellipse((rx - 22, ry - 16, rx + 22, ry + 16), fill=(150, 100, 60))
    d.rounded_rectangle((int(w * .55), int(h * .83), int(w * .93), int(h * .94)), radius=24, fill=WHITE)
    d.text((int(w * .59), int(h * .845)), peso, font=fnt("Black", int(h * .055)), fill=c1)
    im.save(T + f"g2_{nome}.png")

random.seed(3)
# farmácia: antipulgas e carrapatos (concorrentes), vermífugo, medicamentos
caixa("anti_laranja", 600, 900, (226, 104, 28), (247, 160, 60), "Antipulgas", "e carrapatos · cães", "10 a 25 kg")
caixa("anti_azul", 600, 900, (30, 80, 160), (70, 140, 210), "Antipulgas", "spot on · cães", "4 a 10 kg")
caixa("anti_roxo", 600, 900, (96, 52, 140), (150, 100, 190), "Antipulgas", "para gatos", "até 4 kg")
caixa("anti_vinho", 600, 900, (140, 30, 52), (200, 70, 90), "Carrapaticida", "comprimido · cães", "1 unidade")
caixa("verm_amarelo", 1000, 600, (214, 160, 20), (240, 200, 70), "Vermífugo", "cães · 4 comprimidos", "até 10 kg", tom_txt=(40, 30, 10))
caixa("verm_azul", 1000, 600, (20, 110, 150), (60, 170, 200), "Vermífugo", "gatos · 2 comprimidos", "até 5 kg")
caixa("med_cinza", 600, 800, (90, 98, 112), (140, 148, 160), "Uso oral", "10 comprimidos", "cães e gatos")
caixa("med_verde", 600, 800, (30, 130, 110), (80, 180, 150), "Otológico", "solução · 20 mL", "cães e gatos", icone="gota")
caixa("med_petroleo", 600, 800, (14, 90, 100), (50, 140, 150), "Dermatológico", "spray · 100 mL", "cães e gatos", icone="gota")
# suplementos (potes)
rotulo_cilindro("pote_articula", (30, 100, 170), "Suplemento", "articulações · 60 tabletes")
rotulo_cilindro("pote_vitamina", (220, 110, 30), "Vitaminas", "cães · 30 tabletes")
rotulo_cilindro("pote_pelo", (60, 140, 90), "Pele e pelo", "ômega · 30 tabletes")
# higiene do ambiente (concorrentes)
rotulo_cilindro("desinf_azul", (20, 90, 170), "Desinfetante", "pisos e canis · 1 L", icone="gota")
rotulo_cilindro("desinf_lilas", (120, 80, 170), "Eliminador", "de odores · 500 mL", icone="gota")
caixa("tapete", 1200, 800, (40, 120, 190), (110, 180, 230), "Tapete higiênico", "super absorvente", "30 unidades")
saco("areia", (120, 90, 50), (180, 150, 100), "Areia sanitária", "para gatos · grãos finos", "4 kg", icone="graos")
# ração (sacos)
saco("racao_adulto", (170, 30, 40), (220, 70, 70), "Ração premium", "cães adultos · raças médias", "10,1 kg")
saco("racao_filhote", (30, 70, 150), (80, 130, 210), "Ração premium", "filhotes · todas as raças", "10,1 kg")
saco("racao_pele", (30, 120, 90), (80, 180, 140), "Pele sensível", "cães adultos", "7,5 kg")
saco("racao_gato", (200, 130, 20), (240, 180, 70), "Ração para gatos", "adultos castrados", "3 kg")
print("ok")
