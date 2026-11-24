"""Folha de contato dos renders. Uso: python3 tools/folha_contato.py <saida.jpg> SHOT1 SHOT2 ..."""
import sys
from PIL import Image, ImageDraw, ImageFont
out = sys.argv[1]; shots = sys.argv[2:]
h = 360; ims = []
f = ImageFont.truetype("/Users/caiquebecker/Library/Fonts/IBMPlexSans-VariableFont_wdth,wght.ttf", 18)
for s in shots:
    im = Image.open(f"assets/render/{s}.png").convert("RGB")
    im = im.resize((round(im.width * h / im.height), h)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 10 + d.textlength(s, font=f), 26), fill=(0, 0, 0)); d.text((5, 2), s, font=f, fill=(255, 255, 255))
    ims.append(im)
W = 1900; x = y = 8; rowh = 0; sheet = Image.new("RGB", (W, 4000), (255, 255, 255))
for im in ims:
    if x + im.width > W: x = 8; y += rowh + 8; rowh = 0
    sheet.paste(im, (x, y)); x += im.width + 8; rowh = max(rowh, im.height)
sheet.crop((0, 0, W, y + rowh + 8)).save(out, quality=82)
