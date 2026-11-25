"""Guia Ourofino Pet v6 · diagramação de livro: cada slide tem composição própria.
Texto em conteudo-v6/*.md (um bloco === por slide, com @layout). Rodar da raiz:
    python3 tools/v6/livro.py   ->  index.html
Fotos do ensaio: assets/ia/v6-*.png (geradas por tools/v6/ensaio.py) -> assets/img/v6/*.webp"""
import html, os, re, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, os.path.join(ROOT, "tools", "deck")); sys.path.insert(0, os.path.join(ROOT, "tools"))
import build_deck as B
from icones import icone, I as ICONES, CSS as CSS_ICONES

C = os.path.join(ROOT, "conteudo-v6"); IMG = "assets/img/"; V6 = "assets/img/v6/"
esc = lambda s: html.escape(s or "", quote=True)
inl = B.inline

# ------------------------------------------------------------------ fotos do ensaio
def prepara_fotos():
    from PIL import Image
    src = os.path.join(ROOT, "assets/ia"); dst = os.path.join(ROOT, V6); os.makedirs(dst, exist_ok=True)
    for f in sorted(os.listdir(src)):
        if not (f.startswith("v6-") and f.endswith(".png")): continue
        nome = f[:-4]; a = os.path.join(src, f); b = os.path.join(dst, nome + ".webp")
        if os.path.exists(b) and os.path.getmtime(b) > os.path.getmtime(a): continue
        im = Image.open(a).convert("RGB"); w, h = im.size
        alvo = 1800 if w >= h else 1200
        g = im.resize((alvo, round(h * alvo / w)), Image.LANCZOS) if w > alvo or w < alvo else im
        g.save(b, quality=84, method=6)
        im.resize((900, round(h * 900 / w)), Image.LANCZOS).save(os.path.join(dst, nome + "-900.webp"), quality=80, method=6)

def ft(nome, cls="ft", pos="50% 50%", alt="", sizes="100vw"):
    """foto do ensaio v6 ou foto de loja (F-...)"""
    if nome.startswith("F-"):
        return B.img_fig(nome, alt, cls).replace("<img ", f'<img style="object-position:{pos}" ', 1)
    p = os.path.join(ROOT, V6 + nome + ".webp")
    if not os.path.exists(p):
        return f'<span class="{cls} falta" style="object-position:{pos}">foto {esc(nome)}</span>'
    from PIL import Image
    w, h = Image.open(p).size
    return (f'<img class="{cls}" src="{V6}{nome}.webp" srcset="{V6}{nome}-900.webp 900w, {V6}{nome}.webp {w}w" sizes="{sizes}" '
            f'width="{w}" height="{h}" style="object-position:{pos}" alt="{esc(alt)}" loading="lazy" decoding="async">')

def sera(pose, cls="sera"):
    return B.recorte("serafina-" + pose, cls, "Serafina")

# ------------------------------------------------------------------ peças comuns
ULT = 10   # último capítulo numerado
FIM = 11   # fechamento (fechamento.md)
CAPS = {}

def rh(n, claro=False):
    m = CAPS.get(n, {}); t = m.get("titulo", "")
    dir_ = f"{n} · {esc(t)}" if 1 <= n <= ULT else esc(t)
    return f'<header class="rh"><span>Guia de execução no PDV</span><span>{dir_}</span></header>'

def folio():
    return '<footer class="fo"><b data-pagina></b></footer>'

def h2(t, cls="h2"):
    return f'<h2 class="{cls}">{inl(t)}</h2>' if t else ""

def kick(t, cls="kick"):
    return f'<span class="{cls}">{esc(t)}</span>' if t else ""

def txt(corpo, cls="txt"):
    return f'<div class="{cls}">{B.md(corpo)}</div>'

def nota_sf(mk, cls="sf-nota"):
    if not mk.get("dica"): return ""
    return (f'<aside class="{cls}"><span class="sf-av" style="background-image:url({IMG}serafina-explica.webp)" aria-hidden="true"></span>'
            f'<div><b>Dica da Serafina</b><p>{inl(mk["dica"][0])}</p></div></aside>')

def lembre(mk, cls="lb"):
    return f'<p class="{cls}"><b>Lembre-se.</b> {inl(mk["lembre"][0])}</p>' if mk.get("lembre") else ""

def fonte(mk, cls="nf"):
    return f'<p class="{cls}"><sup>1</sup> Fonte: {inl(mk["fonte"][0])}</p>' if mk.get("fonte") else ""

def pratica(mk, cls="np"):
    return f'<p class="{cls}"><b>Na prática.</b> {inl(mk["na-pratica"][0])}</p>' if mk.get("na-pratica") else ""

def legenda(mk, n, k, cls="leg"):
    return f'<p class="{cls}"><b>Fig. {n}.{k}</b> {inl(mk["legenda"][0])}</p>' if mk.get("legenda") else ""

def itens(corpo):
    out = []
    for l in corpo:
        l = re.sub(r"^\d+\.\s*", "", l.strip())
        if not l: continue
        mm = re.match(r"\*\*(.+?)\*\*\s*·\s*(.*)", l)
        if mm: out.append((mm.group(1), mm.group(2)))
    return out

def mais_menos(corpo):
    bons = [l.strip()[1:].strip() for l in corpo if l.strip().startswith("+")]
    maus = [l.strip()[1:].strip() for l in corpo if l.strip().startswith("-")]
    return bons, maus

def ics(mk):
    return [x.split()[0] for x in mk.get("icone", [])]

def ic(nome, cls="ic-s"):
    return f'<span class="{cls}">{icone(nome)}</span>' if nome in ICONES else ""

def validar(notas):
    return B.validar_html(notas)

def pagina(x, cls, inner, tema="papel", sem_rh=False):
    n = x["n"]
    return (f'<section class="slide lv {cls} t-{tema}" id="{x["sid"]}" data-cap="{n:02d}" data-cap-nome="{esc(B.cap_nome(CAPS[n]))}">'
            f'{"" if sem_rh else rh(n)}{inner}{folio()}{validar(x["notas"])}</section>')

# ------------------------------------------------------------------ capas
CAPAS = {
    # painel: lado do texto; tema: cor do painel; pos: janela da foto (o bicho fica inteiro do outro lado)
    1: dict(foto="v6-c01", pos="8% 50%", painel="dir", tema="navy"),
    2: dict(foto="v6-c02", pos="100% 50%", painel="esq", tema="papel"),
    3: dict(foto="v6-c03", pos="90% 50%", painel="dir", tema="navy"),
    4: dict(foto="v6-c04", pos="96% 50%", painel="esq", tema="papel"),
    5: dict(foto="v6-c05", pos="92% 50%", painel="dir", tema="verde"),
    6: dict(foto="v6-c06", pos="96% 70%", painel="esq", tema="papel"),
    7: dict(foto="v6-c07", pos="80% 50%", painel="dir", tema="navy"),
    8: dict(foto="v6-c08", pos="75% 50%", painel="esq", tema="papel"),
    9: dict(foto="v6-c-portfolio", pos="88% 50%", painel="dir", tema="azul"),
    10: dict(foto="v6-c09", pos="85% 50%", painel="esq", tema="navy"),
}

def capa_cap(m, toc=()):
    """abertura de capítulo como num livro: painel de cor com número, título, abertura e o que tem no capítulo; foto do outro lado"""
    n = m["n"]; c = CAPAS[n]
    itens = "".join(f'<li><a href="#{sid}"><span class="cv-it">{inl(t)}</span><i class="sm-dots"></i><span class="sm-p">{{{{PG:{sid}}}}}</span></a></li>' for sid, t in toc)
    tempo = f'<span class="cv-tempo">{esc(m["tempo"])} de leitura</span>' if m.get("tempo") else ""
    painel = (f'<div class="cv-p z"><div class="cv-top"><span class="cv-num">{n:02d}</span><span class="cv-rot">Capítulo {n}<b>{esc(m.get("parte", ""))}</b></span>{tempo}</div>'
              f'{kick(m.get("manuscrito", ""), "cv-kick")}<h2 class="cv-tit">{inl(m["titulo"])}</h2><p class="cv-abre">{inl(m.get("abertura", ""))}</p>'
              f'<nav class="cv-toc" aria-label="Neste capítulo"><b>Neste capítulo</b><ol>{itens}</ol></nav></div>')
    longo = " cv-longo" if len(toc) > 5 else ""
    return (f'<section class="slide lv capa cv cap-{n:02d} cv-{c["painel"]} cv-t-{c["tema"]}{longo}" id="cap{n:02d}" data-cap="{n:02d}" '
            f'data-cap-nome="{esc(B.cap_nome(m))}"><figure class="cv-f z zf">{ft(c["foto"], "ft", c["pos"], m["titulo"])}</figure>{painel}</section>')

def capa_guia():
    return (f'<section class="slide lv capa-guia" id="inicio" data-cap="00" data-cap-nome="Guia de execução no PDV" style="--fundo:#0B1F45">'
            f'<div class="cg-f z zf">{ft("v6-capa", "ft", "70% 50%", "Golden retriever e gato branco")}</div>'
            f'<div class="cg-t z"><img class="cg-logo" src="assets/marca/logo-negativo.svg" alt="Ourofino Saúde Animal" width="320" height="54">'
            f'<span class="cg-kick">seu guia dentro da loja</span><h1>Guia de execução no ponto de venda</h1>'
            f'<p>Da preparação da visita à prateleira ideal. Para promotores, vendedores do distribuidor e equipes de loja da Ourofino Pet.</p>'
            f'<div class="cg-bts"><a class="bt" href="#cap00">Começar {icone("seta")}</a><a class="bt claro" href="#sumario">Sumário</a>'
            f'<button type="button" class="bt claro" data-pdf>Baixar PDF</button></div>'
            f'<span class="cg-ver">Versão 8 · novembro de 2026 · em validação com a Ourofino</span></div></section>')

def prefacio(m):
    """capa da abertura: o nome da Serafina gigante, ela na frente das letras"""
    return (f'<section class="slide lv prefacio t-navy" id="cap00" data-cap="00" data-cap-nome="{esc(B.cap_nome(m))}">'
            f'{B.animais_geo("geo pf-geo z")}<span class="pf-nome z" aria-hidden="true">Serafina</span>'
            f'<div class="pf-sera z">{sera("acena", "pf-img")}</div>'
            f'<span class="pf-kick z">prazer,</span>'
            f'<div class="pf-t z"><span class="pf-cap">00 · Abertura</span><p>{inl(m.get("abertura", ""))}</p></div></section>')

def sumario():
    def item(n):
        m = CAPS[n]; d = f"cap{n:02d}"
        return (f'<li><a href="#{d}"><span class="sm-n">{n}</span><span class="sm-t">{inl(m["titulo"])}</span>'
                f'<i class="sm-dots"></i><span class="sm-p">{{{{PG:{d}}}}}</span></a></li>')
    f = f"cap{FIM:02d}"
    ap = [(f, "Considerações finais"), (f + "-2", "Checklist da visita"), (f + "-3", "Teste final")]
    aps = "".join(f'<li><a href="#{d}"><span class="sm-t">{t}</span><i class="sm-dots"></i><span class="sm-p">{{{{PG:{d}}}}}</span></a></li>' for d, t in ap)
    x = dict(n=0, sid="sumario", notas=[])
    inner = (f'<div class="sm-f z zf">{ft("v6-sumario", "ft", "50% 60%", "Border collie olhando para cima")}</div>'
             f'<div class="sm-q z">{kick("o que tem aqui")}<h2 class="h2 sm-h">Sumário</h2>'
             f'<ol class="sm-l">{"".join(item(n) for n in range(1, ULT + 1))}</ol>'
             f'<div class="sm-fecha"><b>Para fechar</b><ol>{aps}</ol></div></div>')
    return pagina(x, "L-sumario", inner, sem_rh=True)

# ------------------------------------------------------------------ layouts dos slides
def L_carta(x):
    mk, corpo = x["mk"], x["corpo"]
    inner = (f'<span class="ca-aspas z" aria-hidden="true">“</span>'
             f'<div class="ca-q z">{kick("uma carta antes de começar")}{h2(x["titulo"])}<div class="txt col2 capitular">{B.md(corpo)}</div>'
             f'<p class="ca-ass">Serafina<small>promotora da Ourofino Pet há oito anos</small></p></div>'
             f'<figure class="ca-ret z"><div class="ca-folha">{sera("explica", "ca-img")}</div></figure>')
    return pagina(x, "L-carta", inner)

def L_legenda(x):
    it = itens(x["corpo"]); I = ics(x["mk"])
    lis = "".join(f'<li>{ic(I[i] if i < len(I) else "", "lg-ic")}<b>{inl(t)}</b><p>{inl(d)}</p></li>' for i, (t, d) in enumerate(it))
    inner = (f'<div class="lg-lado z">{kick("antes da primeira página")}{h2(x["titulo"])}'
             f'<p class="lead">Seis coisas que ajudam a tirar o melhor do guia, no celular, no treinamento ou no papel.</p>'
             f'<div class="lg-sera">{sera("tablet", "lg-img")}</div></div><ul class="lg-l z">{lis}</ul>')
    return pagina(x, "L-legenda", inner, "papel")

def L_lista_foto(x):
    mk = x["mk"]; it = itens(x["corpo"])
    lis = "".join(f'<li><span class="lf-n">{i + 1}</span><p><b>{inl(t)}.</b> {inl(d)}</p></li>' for i, (t, d) in enumerate(it))
    inner = (f'<figure class="lf-f z zf">{ft(mk["foto"][0], "ft", "50% 50%", "Kit da visita")}{legenda(mk, x["n"], x["k"], "leg sobre")}</figure>'
             f'<div class="lf-q z">{kick("antes de sair")}{h2(x["titulo"])}<ol class="lf-l">{lis}</ol></div>{nota_sf(mk, "sf-nota lf-sf z")}')
    return pagina(x, "L-lista-foto", inner)

def L_trilha(x):
    """os oito passos como tabuleiro de jogo: caminho largo, casas coloridas, início e chegada"""
    it = itens(x["corpo"]); I = ics(x["mk"])
    cols = [150, 500, 850, 1200]
    pos = [(cols[i], 0) for i in range(4)] + [(cols[3 - i], 1) for i in range(4)]
    cores = ["verde", "azul", "ciano", "navy"] * 2
    passos = ""
    for i, (t, d) in enumerate(it):
        xx, row = pos[i]
        passos += (f'<li class="tb-casa r{row} c-{cores[i]}" style="left:{xx}px;--i:{i}"><span class="tb-bola">{ic(I[i] if i < len(I) else "", "tb-ic")}<span class="tb-n">{i + 1}</span></span>'
                   f'<b>{inl(t)}</b><p>{inl(d)}</p></li>')
    caminho = "M96 330 H1300 A155 155 0 0 1 1300 640 H96"
    svg = (f'<svg class="tb-svg z" viewBox="0 0 1600 900" aria-hidden="true">'
           f'<path class="tb-rua" d="{caminho}" fill="none" stroke="#E2F4F8" stroke-width="64" stroke-linecap="round"/>'
           f'<path class="tb-tra" d="{caminho}" fill="none" stroke="#fff" stroke-width="5" stroke-dasharray="18 22" stroke-linecap="round"/></svg>')
    inicio = f'<span class="tb-ini z"><i></i>entrada<br>da loja</span><span class="tb-fim z"><i></i>até a<br>próxima visita</span>'
    inner = f'{svg}{inicio}<div class="tr-cab z">{kick("na loja")}{h2(x["titulo"])}</div><ol class="tb-l z">{passos}</ol>'
    return pagina(x, "L-trilha L-tabuleiro", inner, "papel")

def L_roteiro(x):
    """a chegada como conversa em balões, com a cena da Serafina cumprimentando o balconista"""
    falas = ""; k = 0
    for l in x["corpo"]:
        if ":" not in l: continue
        q, _, f = l.partition(":"); qq = q.strip()
        eu = qq.lower() in ("você", "voce")
        quem = "Você" if eu else qq[:1].upper() + qq[1:]
        falas += (f'<div class="bl{" eu" if eu else ""}" style="--k:{k}"><span class="bl-av" aria-hidden="true"></span>'
                  f'<div class="bl-b"><span class="bl-q">{esc(quem)}</span><p>{inl(f.strip().strip(chr(34)).strip("“”"))}</p></div></div>')
        k += 1
    nota = f'<p class="rt-post z"><b>Lembre-se</b>{inl(x["mk"]["lembre"][0])}</p>' if x["mk"].get("lembre") else ""
    inner = (f'<div class="rt-cena z"><span class="rt-sol"></span>{B.recorte("cena-chegada-sem-fundo", "rt-cimg", "Serafina cumprimenta o balconista")}<span class="rt-balcao"><i></i></span><span class="rt-piso"></span></div>'
             f'<div class="rt-cab z">{kick("roteiro da chegada")}{h2(x["titulo"])}</div><div class="rt-chat z">{falas}</div>{nota}')
    return pagina(x, "L-roteiro L-chat", inner)

def L_faixa_foto(x):
    mk = x["mk"]; it = itens(x["corpo"]); I = ics(mk)
    lis = "".join(f'<li><span class="ff-n">{i + 1}</span><b>{inl(t)}</b><p>{inl(d)}</p></li>' for i, (t, d) in enumerate(it))
    q = mk["lembre"][0] if mk.get("lembre") else ""
    inner = (f'<figure class="ff-f z zf">{ft(mk["foto"][0], "ft", "50% 55%", "Promotora fotografando a prateleira")}</figure>'
             f'<div class="ff-cab z">{kick("depois da visita")}{h2(x["titulo"])}</div>'
             f'<blockquote class="ff-cit z">{inl(q)}</blockquote><ol class="ff-l z">{lis}</ol>')
    return pagina(x, "L-faixa-foto", inner, sem_rh=True)

def L_numero(x):
    mk = x["mk"]; dado = mk["dado"][0]; num = re.search(r"\d+(?:,\d+)?\s?%", dado).group(0)
    inner = (f'<div class="nu-n z" aria-hidden="true">{esc(num.replace(" ", ""))}</div>'
             f'<p class="nu-d z">{inl(dado)}<sup>1</sup></p>'
             f'<div class="nu-q z">{kick("por que importa")}{h2(x["titulo"])}{txt(x["corpo"])}</div>{fonte(mk, "nf nu-nf z")}')
    return pagina(x, "L-numero", inner, "navy")

def L_cadeia(x):
    mk = x["mk"]
    nos = [("fabrica", "Ourofino", "fabrica o produto"), ("caminhao", "Distribuidor", "compra, estoca e entrega"),
           ("loja", "Loja", "expõe, orienta e vende"), ("casa", "Tutor", "leva para casa e cuida do pet")]
    setas = [("abastece", ""), ("sell-in", "v"), ("sell-out", "a")]
    h = ""
    for i, (icn, t, s) in enumerate(nos):
        h += f'<li class="cd-no"><span class="cd-ic">{icone(icn)}</span><b>{t}</b><small>{s}</small></li>'
        if i < 3: h += f'<li class="cd-seta {setas[i][1]}" aria-hidden="true"><span>{setas[i][0]}</span></li>'
    inner = (f'<div class="cd-cab z">{kick("o caminho do produto")}{h2(x["titulo"])}</div><div class="cd-txt z">{B.md(x["corpo"])}</div>'
             f'<div class="cd-faixa z"><ol class="cd-l">{h}</ol>{pratica(mk, "np cd-np")}</div>')
    return pagina(x, "L-cadeia", inner)

def L_dicionario(x):
    ents = ""
    for l in x["corpo"]:
        mm = re.match(r"\*\*(.+?)\*\*\s*(?:_(.+?)_)?\s*·\s*(.*)", l.strip())
        if mm: ents += f'<div class="dc-e"><dt><b>{inl(mm.group(1))}</b>{f"<i>{esc(mm.group(2))}</i>" if mm.group(2) else ""}</dt><dd>{inl(mm.group(3))}</dd></div>'
    inner = (f'<span class="dc-aa z" aria-hidden="true">Aa</span><div class="dc-cab z">{kick("pequeno dicionário do trade")}{h2(x["titulo"])}</div>'
             f'<dl class="dc-l z">{ents}</dl>')
    return pagina(x, "L-dicionario", inner)

def L_waffle(x):
    mk = x["mk"]; partes = [(int(p.split("|")[0]), p.split("|")[1].strip()) for p in mk["parte"]]
    cores = ["#072047", "#007CC1", "#20D5F2", "#C9CED6", "#10AD31"]
    cel = ""; cum = 0; legs = ""
    for i, (v, t) in enumerate(partes):
        cel += f'<i style="background:{cores[i]}"></i>' * v
        legs += f'<li style="left:{cum}%;width:{max(v, 11)}%"><b style="color:{cores[i] if i not in (2, 3) else "#072047"}">{v}</b><span>{esc(t)}</span></li>'
        cum += v
    inner = (f'<div class="wf-cab z">{kick("o custo da falta")}{h2(x["titulo"])}</div><div class="wf-txt z">{txt(x["corpo"])}{fonte(mk)}</div>'
             f'<p class="wf-d z">{inl(mk["dado"][0])}<sup>1</sup></p><div class="wf-g z" aria-hidden="true">{cel}</div><ol class="wf-leg z">{legs}</ol>')
    return pagina(x, "L-waffle", inner)

def L_quatro(x):
    mk = x["mk"]; it = itens(x["corpo"]); I = ics(mk)
    it = [(re.sub(r"^\d+\.\s*", "", t), d) for t, d in it]
    lis = "".join(f'<li><span class="qt-n">{i + 1}</span>{ic(I[i] if i < len(I) else "", "qt-ic")}<b>{inl(t)}</b><p>{inl(d)}</p></li>' for i, (t, d) in enumerate(it))
    inner = (f'<figure class="qt-f z zf">{ft(mk["foto"][0], "ft", "50% 50%", "Mãos alinhando caixas na prateleira")}</figure>'
             f'<div class="qt-cab z">{kick("na gôndola")}{h2(x["titulo"])}{nota_sf(mk, "sf-nota qt-sf")}</div><ol class="qt-l z">{lis}</ol>')
    return pagina(x, "L-quatro", inner, sem_rh=True)

def L_diagrama_lateral(x):
    mk = x["mk"]; fid = mk["fig"][0].split()[0]
    inner = (f'<div class="dl-q z">{kick("validade")}{h2(x["titulo"])}{txt(x["corpo"])}{fonte(mk)}</div>'
             f'<figure class="dl-f z"><div class="dg-caixa">{B.diagrama(fid)}</div><p class="leg"><b>Fig. {x["n"]}.{x["k"]}</b> Ao repor, a caixa que vence antes vai para a frente.</p></figure>')
    return pagina(x, "L-diagrama-lateral", inner, "n1")

def L_diagrama_dado(x):
    mk = x["mk"]; fid = mk["fig"][0].split()[0]; nn, nt = [s.strip() for s in mk["numero"][0].split("|")]
    inner = (f'<figure class="dd-f z"><div class="dg-caixa">{B.diagrama(fid)}</div></figure>'
             f'<div class="dd-q z">{kick("frente e bloco")}{h2(x["titulo"])}{txt(x["corpo"])}'
             f'<p class="dd-n"><b>+{esc(nn)}</b><span>{esc(nt)}<sup>1</sup></span></p>{fonte(mk)}</div>')
    return pagina(x, "L-diagrama-dado", inner)

def L_alturas(x):
    mk = x["mk"]; fid = mk["fig"][0].split()[0]
    faixas = [("alta", "acima de 1,60 m", "vista, mas pede esforço", 140, 250), ("quente", "1,20 m a 1,60 m", "onde o olhar cai primeiro", 250, 430),
              ("media", "0,80 m a 1,20 m", "ao alcance da mão", 430, 590), ("baixa", "abaixo de 0,80 m", "o tutor precisa se abaixar", 590, 800)]
    fx = "".join(f'<div class="al-fx {c}" style="top:{a}px;height:{b - a}px"><b>{t}</b><small>{s}</small></div>' for c, t, s, a, b in faixas)
    inner = (f'<div class="al-q z">{kick("as três alturas")}{h2(x["titulo"])}{txt(x["corpo"])}{fonte(mk)}</div>'
             f'<div class="al-regua z" aria-hidden="true">{fx}<span class="al-chao">chão</span></div>'
             f'<figure class="al-f z zf">{ft(fid, "ft", "50% 50%", "Gôndola com as três alturas")}</figure>')
    return pagina(x, "L-alturas", inner)

def L_comparador_cheio(x):
    mk = x["mk"]; f = [y.split()[0] for y in mk["fig"]]
    inner = (f'<div class="cc-comp z zf">{B.visual_fig(f, x["titulo"])}</div>'
             f'<div class="cc-cx z">{kick("arraste para comparar")}<h3>{inl(x["titulo"])}</h3>{txt(x["corpo"])}{lembre(mk)}</div>')
    return pagina(x, "L-comparador-cheio", inner, sem_rh=True)

def L_catalogo(x):
    its = ""
    for i, l in enumerate([l for l in x["corpo"] if "|" in l]):
        esq, _, d = l.partition("|"); pp = esq.split(); fid = pp[0]; pos = " ".join(pp[1:]) or "50% 50%"
        mm = re.match(r"\s*\*\*(.+?)\*\*\s*·\s*(.*)", d)
        its += (f'<li><div class="ct-img">{ft(fid, "ft", pos, mm.group(1))}</div><div><span class="ct-n">{i + 1}</span>'
                f'<b>{inl(mm.group(1))}</b><p>{inl(mm.group(2))}</p></div></li>')
    inner = (f'<div class="ct-cab z">{kick("materiais de prateleira")}{h2(x["titulo"])}'
             f'<p class="lead ct-lead">Cada peça tem um lugar e uma função. Longe do produto, nenhuma delas funciona.</p></div><ul class="ct-l z">{its}</ul>')
    return pagina(x, "L-catalogo", inner)

def L_filme(x):
    its = ""; caps = ""
    for i, l in enumerate([l for l in x["corpo"] if "|" in l]):
        esq, _, d = l.partition("|"); pp = esq.split(); fid = pp[0]; pos = " ".join(pp[1:]) or "50% 50%"
        mm = re.match(r"\s*\*\*(.+?)\*\*\s*·\s*(.*)", d)
        its += f'<div class="fm-q"><span class="fm-n">{i + 7}</span>{ft(fid, "ft", pos, mm.group(1))}</div>'
        caps += f'<li><b>{inl(mm.group(1))}</b><p>{inl(mm.group(2))}</p></li>'
    inner = (f'<div class="fm-cab z">{kick("fora da prateleira")}{h2(x["titulo"])}</div>'
             f'<div class="fm-tira z zf">{its}</div><ol class="fm-l z">{caps}</ol>')
    return pagina(x, "L-filme", inner)

def L_erro(x):
    j = " ".join(l.strip() for l in x["corpo"])
    mm = re.match(r"\*\*O que acontece:\*\*(.*?)\*\*Faça assim:\*\*(.*)", j, re.S)
    a, b = mm.group(1).strip(), mm.group(2).strip()
    inner = (f'<div class="er-sera z">{sera("atencao")}</div>'
             f'<div class="er-q z"><span class="er-k">erro comum</span>{h2(x["titulo"])}'
             f'<div class="er-a"><b>{icone("errado")}O que acontece</b><p>{inl(a)}</p></div>'
             f'<div class="er-b"><b>{icone("certo")}Faça assim</b><p>{inl(b)}</p></div></div>{lembre(x["mk"], "lb er-lb z")}')
    return pagina(x, "L-erro", inner, "n1")

def L_definicoes(x):
    mk = x["mk"]; it = itens(x["corpo"])
    defs = "".join(f'<div class="df-d"><span class="df-g">{"termo do trade"}</span><b>{inl(t)}</b><p>{inl(d)}</p></div>' for t, d in it[:2])
    notas = "".join(f'<div class="df-n"><span class="kick">{esc(t.lower())}</span><p>{inl(d)}</p></div>' for t, d in it[2:])
    inner = (f'<div class="df-cab z">{kick("cruzar")}{h2(x["titulo"])}</div><div class="df-defs z">{defs}</div><div class="df-notas z">{notas}</div>'
             f'<figure class="df-f z zf">{ft(mk["foto"][0], "ft", "50% 50%", "Gato cheirando sacos de areia")}{legenda(mk, x["n"], x["k"], "leg sobre")}</figure>')
    return pagina(x, "L-definicoes", inner, sem_rh=False)

def L_mapa(x):
    mk = x["mk"]; fid = mk["fig"][0].split()[0]
    inner = (f'<div class="mp-q z">{kick("onde cruzar")}{h2(x["titulo"])}{txt(x["corpo"])}{fonte(mk)}</div>'
             f'<figure class="mp-f z"><div class="dg-caixa">{B.diagrama(fid)}</div></figure>')
    return pagina(x, "L-mapa", inner, "n1")

def L_foto_painel(x):
    mk = x["mk"]; fid = mk["fig"][0].split()[0]
    inner = (f'<figure class="fp-f z zf">{ft(fid, "ft", "70% 50%", x["titulo"])}</figure>'
             f'<div class="fp-p z"><span class="er-k">erro comum</span>{h2(x["titulo"])}{txt(x["corpo"])}{lembre(mk)}</div>')
    return pagina(x, "L-foto-painel", inner, sem_rh=True)

def L_comparador_quadro(x):
    mk = x["mk"]; f = [y.split()[0] for y in mk["fig"]]; nn, nt = [s.strip() for s in mk["numero"][0].split("|")]
    inner = (f'<div class="cq-q z">{kick("certo e errado")}{h2(x["titulo"])}{txt(x["corpo"])}'
             f'<p class="dd-n"><b>+{esc(nn)}</b><span>{esc(nt)}<sup>1</sup></span></p>{fonte(mk)}</div>'
             f'<div class="cq-comp z">{B.visual_fig(f, x["titulo"])}</div>')
    return pagina(x, "L-comparador-quadro", inner)

def L_escada(x):
    mk = x["mk"]; it = itens(x["corpo"]); I = ics(mk)
    lis = "".join(f'<li style="--h:{250 + i * 52}px"><span class="es-n">{i + 1}</span>{ic(I[i] if i < len(I) else "", "es-ic")}<b>{inl(t)}</b><p>{inl(d)}</p></li>' for i, (t, d) in enumerate(it))
    inner = f'<div class="es-cab z">{kick("passo a passo")}{h2(x["titulo"])}</div>{nota_sf(mk, "sf-nota es-sf z")}<ol class="es-l z">{lis}</ol>'
    return pagina(x, "L-escada", inner)

def L_etiqueta(x):
    mk = x["mk"]; it = itens(x["corpo"])
    lis = "".join(f'<li><span class="et-n">{i + 1}</span><b>{inl(t)}</b><p>{inl(d)}</p></li>' for i, (t, d) in enumerate(it))
    inner = (f'<figure class="et-f z zf">{ft(mk["foto"][0], "ft", "35% 50%", "Tutora com cão no balcão do petshop")}</figure>'
             f'<div class="et-q z">{kick("na casa dos outros")}{h2(x["titulo"])}<ol class="et-l">{lis}</ol></div>')
    return pagina(x, "L-etiqueta", inner, sem_rh=True)

def L_citacoes(x):
    mk = x["mk"]; it = itens(x["corpo"]); I = ics(mk)
    cols = ""
    for i, (t, d) in enumerate(it):
        mm = re.match(r'"([^"]+)"\s*(.*)', d)
        q, resto = (mm.group(1), mm.group(2)) if mm else ("", d)
        cols += f'<div class="cz-c"><span class="cz-a" aria-hidden="true">“</span><blockquote>{esc(q)}</blockquote><b>{ic(I[i] if i < len(I) else "", "cz-ic")}{inl(t)}</b><p>{inl(resto)}</p></div>'
    inner = f'<div class="cz-cab z">{kick("o que o lojista diz")}{h2(x["titulo"])}</div>{nota_sf(mk, "sf-nota cz-sf z")}<div class="cz-l z">{cols}</div>'
    return pagina(x, "L-citacoes", inner)

def rotula_tabela(h):
    """põe o nome da coluna em cada célula (data-th), para a tabela virar cartões no celular"""
    ths = [re.sub(r"<.*?>", "", t).strip() for t in re.findall(r"<th[^>]*>(.*?)</th>", h, flags=re.S)]
    def linha(m):
        k = [0]
        def cel(c):
            i = k[0]; k[0] += 1
            return f'<td data-th="{esc(ths[i]) if i < len(ths) else ""}"' if i else '<td class="tf-rot"'
        return re.sub(r"<td", cel, m.group(0))
    return re.sub(r"<tr>.*?</tr>", linha, h, flags=re.S)

def L_tabela_foto(x):
    mk = x["mk"]
    inner = (f'<div class="tf-q z">{kick("quem decide")}{h2(x["titulo"])}<div class="tf-t">{rotula_tabela(B.md(x["corpo"]))}</div>{lembre(mk)}</div>'
             f'<figure class="tf-f z zf">{ft(mk["foto"][0], "ft", "50% 40%", "Veterinária com gato no colo")}{legenda(mk, x["n"], x["k"], "leg sobre")}</figure>')
    return pagina(x, "L-tabela-foto", inner)

def L_sempre_nunca(x):
    bons, maus = mais_menos(x["corpo"])
    lb = lambda L, i: "".join(f'<li>{icone(i)}<span>{inl(y)}</span></li>' for y in L)
    inner = (f'<div class="sn-cab z">{kick("postura em campo")}{h2(x["titulo"])}</div>'
             f'<div class="sn-c sn-s z"><h3>Sempre</h3><ul>{lb(bons, "certo")}</ul></div>'
             f'<div class="sn-c sn-n z"><h3>Nunca</h3><ul>{lb(maus, "errado")}</ul></div>{lembre(x["mk"], "lb sn-lb z")}')
    return pagina(x, "L-sempre-nunca", inner)

def L_cbv(x):
    mk = x["mk"]
    deg = [("C", "Característica", "o que o produto é", mk["c"][0]), ("B", "Benefício", "o que muda para o pet e o tutor", mk["b"][0]),
           ("V", "Vantagem", "por que escolher este", mk["v"][0])]
    h = "".join(f'<li class="cb-d d{i}"><span class="cb-l">{l}</span><b>{t}</b><small>{s}</small><p>{inl(e)}</p>{"<span class=cb-e>e daí?</span>" if i < 2 else ""}</li>' for i, (l, t, s, e) in enumerate(deg))
    inner = (f'<div class="cb-q z">{kick("como falar")}{h2(x["titulo"])}{txt(x["corpo"])}{pratica(mk)}</div>'
             f'<figure class="cb-f z zf">{ft(mk["foto"][0], "ft", "50% 50%", "Cão pegando petisco da mão")}</figure><ol class="cb-esc z">{h}</ol>')
    return pagina(x, "L-cbv", inner, sem_rh=True)

def prods(corpo):
    out = []
    for l in corpo:
        if l.count("|") < 4: continue
        fid, nome, tag, desc, frase = [y.strip() for y in l.split("|", 4)]
        out.append((fid, re.sub(r"[*]", "", nome), tag, desc, frase))
    return out

def L_produtos4(x):
    lis = "".join(f'<li><div class="p4-img">{B.img_fig(fid, nome)}</div><span class="p4-tag">{esc(tag)}</span><b>{esc(nome)}</b><p>{inl(desc)}</p>'
                  f'<p class="p4-fr"><span>No balcão</span>{inl(fr)}</p></li>' for fid, nome, tag, desc, fr in prods(x["corpo"]))
    inner = f'<div class="p4-cab z">{kick("produtos heróis")}{h2(x["titulo"])}<p class="lead">Os quatro que protegem o pet de parasitas.</p></div><ul class="p4-l z">{lis}</ul>'
    return pagina(x, "L-produtos4", inner, "n1")

def L_produtos_linhas(x):
    mk = x["mk"]
    lis = "".join(f'<li><div class="pl-img">{B.img_fig(fid, nome)}</div><div class="pl-t"><span class="p4-tag">{esc(tag)}</span><b>{esc(nome)}</b><p>{inl(desc)}</p></div>'
                  f'<blockquote class="pl-fr"><span>No balcão</span>{inl(fr)}</blockquote></li>' for fid, nome, tag, desc, fr in prods(x["corpo"]))
    inner = (f'<figure class="pl-f z zf">{ft(mk["foto"][0], "ft", "86% 50%", "Filhote no tapete higiênico")}{legenda(mk, x["n"], x["k"], "leg sobre")}</figure>'
             f'<div class="pl-q z">{kick("produtos heróis")}{h2(x["titulo"])}<ul class="pl-l">{lis}</ul></div>')
    return pagina(x, "L-produtos-linhas", inner, sem_rh=True)

def L_pode_nao(x):
    mk = x["mk"]; bons, maus = mais_menos(x["corpo"])
    lb = lambda L, i: "".join(f'<li>{icone(i)}<span>{inl(y)}</span></li>' for y in L)
    inner = (f'<figure class="pn-f z zf">{ft(mk["foto"][0], "ft", "50% 60%", "Gato olhando para a câmera")}</figure>'
             f'<div class="pn-q z">{kick("o limite da conversa")}{h2(x["titulo"])}<div class="pn-g"><div class="pn-c ok"><h3>Pode</h3><ul>{lb(bons, "certo")}</ul></div>'
             f'<div class="pn-c no"><h3>Não pode</h3><ul>{lb(maus, "errado")}</ul></div></div>{lembre(mk)}</div>')
    return pagina(x, "L-pode-nao", inner, sem_rh=True)

def L_figura_pinos(x):
    mk = x["mk"]; fid = mk["fig"][0].split()[0]; rot = B.V3.rotulos(fid)
    inner = (f'<div class="fq-q z">{kick("a prateleira ideal")}{h2(x["titulo"])}{txt(x["corpo"])}'
             f'<p class="leg"><b>Fig. {x["n"]}.{x["k"]}</b> Os pontos mostram o que cada bloco resolve.</p></div>'
             f'<figure class="fq-f z zf"><div class="foto-q">{B.img_fig(fid, x["titulo"])}<div class="rot">{rot}</div>'
             f'<button class="rot-btn" type="button">Ocultar marcações</button></div></figure>')
    return pagina(x, "L-figura-pinos", inner, "n1", sem_rh=True)

def L_regras(x):
    mk = x["mk"]; it = itens(x["corpo"])
    lis = "".join(f'<li><span class="rg-n">{i + 1}</span><b>{inl(t)}</b><p>{inl(d)}</p></li>' for i, (t, d) in enumerate(it))
    inner = (f'<figure class="rg-f z zf">{ft(mk["foto"][0], "ft", "50% 50%", "Cão passeando de coleira")}{nota_sf(mk, "sf-nota rg-sf")}</figure>'
             f'<div class="rg-q z">{kick("cinco regras")}{h2(x["titulo"])}<ol class="rg-l">{lis}</ol></div>')
    return pagina(x, "L-regras", inner, sem_rh=True)

def L_epilogo(x):
    corpo = [l for l in x["corpo"] if l.strip()]
    prim = re.split(r"(?<=[.:])\s", corpo[0], 1)
    cit = prim[0]; resto = [prim[1]] + corpo[1:] if len(prim) > 1 else corpo[1:]
    inner = (f'<div class="ep-q z">{kick("para fechar")}{h2(x["titulo"])}<blockquote class="ep-cit">{inl(cit)}</blockquote>'
             f'<div class="txt">{B.md(resto)}</div><p class="ca-ass">Serafina<small>até a próxima loja</small></p></div>'
             f'<div class="ep-sera z">{sera("joinha", "ep-img")}</div>{B.animais_geo("geo ep-geo z")}')
    return pagina(x, "L-epilogo", inner, "navy")

def L_reuso(x, tipo):
    """checklist e teste: aproveita a marcação da v5 e troca o cabeçalho"""
    s = B.slide(CAPS[x["n"]], x["k"], tipo, x["titulo"], x["linhas"], x["notas"])
    s = re.sub(r'<header class="cab">.*?</footer>', rh(x["n"]) + folio(), s, count=1, flags=re.S)
    s = s.replace('class="slide s-', 'class="slide lv L-' + tipo + ' s-', 1).replace(f'id="cap{x["n"]:02d}-{x["k"]}"', f'id="{x["sid"]}"', 1)
    return s

def L_contracapa(x):
    mk = x["mk"]
    return (f'<section class="slide lv contracapa" id="fim" data-cap="{FIM}" data-cap-nome="{esc(B.cap_nome(CAPS[FIM]))}" style="--fundo:#0B1F45">'
            f'<div class="cg-f z zf">{ft(mk["foto"][0], "ft", "70% 50%", "Filhotes de cão e gato dormindo juntos")}</div>'
            f'<div class="cg-t z"><img class="cg-logo" src="assets/marca/logo-negativo.svg" alt="Ourofino Saúde Animal" width="320" height="54">'
            f'<span class="cg-kick">obrigada pela visita</span><h1>{inl(x["titulo"])}</h1>{B.md(x["corpo"])}'
            f'<div class="cg-bts"><a class="bt" href="#inicio">Voltar ao início</a><a class="bt claro" href="#cap{FIM:02d}-2">Checklist</a>'
            f'<button type="button" class="bt claro" data-pdf>Baixar PDF</button></div>'
            f'<span class="cg-ver">Guia de execução no PDV · Ourofino Pet · versão 8, novembro de 2026</span></div></section>')

# ------------------------------------------------------------------ v8: planta da clínica e categoria
def planta_clinica_svg():
    N, V, CZ, LN = "#072047", "#10AD31", "#7A8597", "#C9CFD8"
    t = lambda x, y, txt, cls="pc-z", anc="middle": f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anc}">{txt}</text>'
    o = ['<svg class="pc-svg" viewBox="0 0 860 600" role="img" aria-label="Planta de uma clínica veterinária com petshop: recepção e farmácia na entrada, sala de espera no meio, consultórios ao fundo e área de petshop">']
    o.append(f'<rect x="20" y="20" width="820" height="540" rx="6" fill="#FBFAF7" stroke="{N}" stroke-width="6"/>')
    # consultórios
    for i, x0 in enumerate((20, 300, 580)):
        w = 280 if i < 2 else 260
        o.append(f'<rect x="{x0}" y="20" width="{w}" height="170" fill="#EEF1F5" stroke="{N}" stroke-width="3"/>')
        o.append(t(x0 + w / 2, 100, f"Consultório {i + 1}", "pc-z"))
        o.append(f'<rect x="{x0 + w / 2 - 34}" y="186" width="68" height="8" fill="#FBFAF7"/><path d="M{x0 + w / 2 - 34} 190 a68 68 0 0 1 68 -68" fill="none" stroke="{LN}" stroke-width="2"/>')
    # recepção e farmácia
    o.append(f'<rect x="32" y="232" width="26" height="300" fill="#DDE7D9" stroke="{N}" stroke-width="2"/>')
    for k in range(6): o.append(f'<rect x="36" y="{240 + k * 48}" width="18" height="38" rx="2" fill="{["#10AD31", "#007CC1", "#20D5F2"][k % 3]}" opacity=".85"/>')
    o.append(f'<path d="M110 286 h120 v24 h-96 v130 h-24 z" fill="#fff" stroke="{N}" stroke-width="3"/>')
    o.append(t(84, 552, "FARMÁCIA", "pc-r", "start")); o.append(t(176, 272, "RECEPÇÃO", "pc-r"))
    # sala de espera
    o.append(t(560, 236, "SALA DE ESPERA", "pc-r"))
    for fila in (270, 330):
        for k in range(7): o.append(f'<rect x="{350 + k * 58}" y="{fila}" width="40" height="34" rx="8" fill="#fff" stroke="{LN}" stroke-width="2"/>')
    o.append(f'<rect x="832" y="250" width="8" height="90" fill="{V}"/>')
    # petshop
    o.append(f'<rect x="520" y="430" width="300" height="20" fill="#E9EDF2" stroke="{N}" stroke-width="2"/><rect x="520" y="512" width="300" height="20" fill="#E9EDF2" stroke="{N}" stroke-width="2"/>')
    o.append(t(640, 482, "PETSHOP · ração e acessórios", "pc-r"))
    # entrada
    o.append(f'<rect x="300" y="554" width="120" height="12" fill="#FBFAF7"/>')
    o.append(t(360, 590, "ENTRADA", "pc-r"))
    # caminho do tutor
    ida = "M330 572 V430 L262 362 L520 300 L440 200"
    volta = "M440 200 L404 300 L262 404 L92 470 L300 532 L390 572"
    cam = ida + " " + volta.replace("M", "L", 1)
    o.append(f'<path d="{ida}" fill="none" stroke="{V}" stroke-width="3.5" stroke-dasharray="3 10" stroke-linecap="round" stroke-linejoin="round"/>')
    o.append(f'<path d="{volta}" fill="none" stroke="#007CC1" stroke-width="3.5" stroke-dasharray="3 10" stroke-linecap="round" stroke-linejoin="round"/>')
    o.append(t(560, 588, "— chegada", "pc-k1", "start").replace("— ", "")); o.append(t(660, 588, "saída", "pc-k2", "start"))
    o.append(f'<path d="M538 583 h16" stroke="{V}" stroke-width="4" stroke-dasharray="3 5"/><path d="M638 583 h16" stroke="#007CC1" stroke-width="4" stroke-dasharray="3 5"/>')
    o.append(f'<g class="pc-tutor"><circle r="13" fill="{V}" stroke="#fff" stroke-width="4"/><animateMotion dur="9s" repeatCount="indefinite" path="{cam}" rotate="0"/></g>')
    # pinos
    def pino(x, y, n, cor=V):
        return f'<g class="pc-pino"><circle cx="{x}" cy="{y}" r="19" fill="{cor}" stroke="#fff" stroke-width="4"/><text x="{x}" y="{y + 6}" text-anchor="middle" class="pc-n">{n}</text></g>'
    o += [pino(176, 330, 1), pino(806, 296, 2), pino(46, 470, 3), pino(800, 482, 4), pino(440, 64, "✕", N)]
    o.append('</svg>')
    return "".join(o)

def L_planta_clinica(x):
    mk = x["mk"]
    pts = []
    for pnt in mk.get("ponto", []):
        n, nome, d = [y.strip() for y in pnt.split("|", 2)]
        cls = " nao" if n.lower() == "x" else ""
        pts.append(f'<li class="pc-i{cls}"><span>{"✕" if cls else n}</span><p><b>{esc(nome)}.</b> {inl(d)}</p></li>')
    inner = (f'<div class="pc-q z">{kick("na clínica")}{h2(x["titulo"])}{txt(x["corpo"])}<ol class="pc-l">{"".join(pts)}</ol>{lembre(mk)}</div>'
             f'<figure class="pc-f z">{planta_clinica_svg()}{legenda(mk, x["n"], x["k"])}</figure>')
    return pagina(x, "L-planta-clinica", inner, "n1")

def L_categoria(x):
    mk = x["mk"]
    lst = lambda L: "".join(f'<li>{icone("certo")}<span>{inl(y)}</span></li>' for y in L)
    falas = "".join(f'<li><b>{esc(a.split("|")[0].strip())}</b><span>{inl(a.split("|", 1)[1].strip())}</span></li>' for a in mk.get("fala", []))
    inner = (f'<div class="ca2-q z">{kick("uma semente")}{h2(x["titulo"])}{txt(x["corpo"])}'
             f'<h3 class="ca2-h">Como falar disso na loja</h3><ul class="ca2-falas">{falas}</ul>{pratica(mk)}</div>'
             f'<figure class="ca2-f z zf">{ft(mk["foto"][0], "ft", "50% 40%", "Shih-tzu sentado numa cesta de compras")}</figure>'
             f'<div class="ca2-p z"><div><h3>O tutor ganha</h3><ul>{lst(mk.get("tutor", []))}</ul></div>'
             f'<div><h3>A loja ganha</h3><ul>{lst(mk.get("loja", []))}</ul></div></div>')
    return pagina(x, "L-categoria", inner)

# ------------------------------------------------------------------ capítulo 9: os 10 de cada categoria (fichas CBV)
PK = "assets/img/pk/"
CBV3 = (("c", "C", "Característica"), ("b", "B", "Benefício"), ("v", "V", "Vantagem"))

def ficha_l(l):
    p = [y.strip() for y in l.split("|")]
    if len(p) < 7: return None
    return dict(pk=p[0], nome=p[1], esp=p[2], flags=p[3].split(), c=p[4], b=p[5], v=p[6])

def fichas(corpo):
    """[(grupo, [ficha])]; linhas '## Grupo' abrem grupo"""
    gr = [[None, []]]
    for l in corpo:
        s = l.strip()
        if s.startswith("## "):
            gr.append([s[3:].strip(), []]); continue
        f = ficha_l(s)
        if f: gr[-1][1].append(f)
    return [g for g in gr if g[1]]

def pk_img(f, cls="fx-pk"):
    p = os.path.join(ROOT, PK + f["pk"] + ".webp")
    if not os.path.exists(p): return f'<span class="{cls} falta">{esc(f["nome"])}</span>'
    from PIL import Image
    w, h = Image.open(p).size
    return f'<img class="{cls}" src="{PK}{f["pk"]}.webp" width="{w}" height="{h}" alt="Embalagem de {esc(f["nome"])}" loading="lazy" decoding="async">'

def selos(f):
    s = ""
    if "heroi" in f["flags"]: s += '<span class="fx-heroi" title="Produto herói, capítulo 8">herói</span>'
    if "receita" in f["flags"]: s += '<span class="fx-rx" title="Medicamento: sai com orientação do veterinário">com receita</span>'
    return s

def fx_cbv(f, rotulo=False, notas=None):
    notas = notas or {}
    return '<dl class="fx-cbv">' + "".join(
        f'<div class="fx-{k}"><dt title="{t}"><span class="fx-L">{L}</span>{f"<small>{t}</small>" if rotulo else ""}</dt><dd>{inl(f[k])}</dd>{notas.get(k, "")}</div>' for k, L, t in CBV3) + "</dl>"

def ficha(f, cls="fx", notas=None, rotulo=False):
    notas = notas or {}
    fl = " ".join("is-" + x for x in f["flags"])
    return (f'<article class="{cls} {fl}"><div class="fx-img">{pk_img(f)}{notas.get("img", "")}</div>'
            f'<div class="fx-t"><header class="fx-cab"><b class="fx-n">{esc(f["nome"])}</b><span class="fx-esp">{esc(f["esp"])}</span>{selos(f)}{notas.get("cab", "")}</header>'
            f'{fx_cbv(f, rotulo, notas)}</div></article>')

def cat_cab(x, n_total, pagina=""):
    """cabeça de categoria: chamada, título, contagem"""
    mk = x["mk"]
    num = (f'<div class="ct-num"><span>{n_total:02d}</span><small>produtos{pagina}</small></div>') if n_total else ""
    lead = f'<p class="lead">{inl(mk["lead"][0])}</p>' if mk.get("lead") else ""
    return (kick("categoria") + h2(x["titulo"]) + lead, num)

def linha_extra(mk, cls="fx-linha"):
    return f'<p class="{cls}">{inl(mk["linha"][0])}</p>' if mk.get("linha") else ""

def L_fichas_guia(x):
    mk = x["mk"]; ex = ficha_l(mk["exemplo"][0])
    call = lambda t: f'<i class="fg-c"><b>{t}</b></i>'
    ex_html = ficha(ex, "fx fx-ex", {"img": call("A embalagem, como está na loja"), "cab": call("Nome, espécie e selo"),
                                      "c": call("O que o produto é"), "b": call("O que muda para o pet e o tutor"), "v": call("Por que escolher este")}, rotulo=True)
    cats = []
    for c in mk.get("cat", []):
        nome, n, alvo = [y.strip() for y in c.split("|")]
        cats.append(f'<li><a href="#{alvo}"><span class="fg-k">{int(n):02d}</span><span class="fg-t">{esc(nome)}</span><i class="sm-dots"></i><span class="sm-p">{{{{PG:{alvo}}}}}</span></a></li>')
    inner = (f'<div class="fg-q z">{kick("antes das fichas")}{h2(x["titulo"])}{txt(x["corpo"])}'
             f'<ol class="fg-cats">{"".join(cats)}</ol>'
             f'<p class="fg-selos"><span class="fx-heroi">herói</span> produto do capítulo 8 <span class="fx-rx">com receita</span> medicamento: sai com orientação do veterinário</p></div>'
             f'<div class="fg-ex z">{ex_html}</div>')
    return pagina(x, "L-fichas-guia", inner)

def L_fichas_grade(x):
    g = fichas(x["corpo"]); fs = [f for _, L in g for f in L]
    cab, num = cat_cab(x, len(fs))
    inner = (f'<div class="fr-cab z"><div>{cab}{linha_extra(x["mk"])}</div>{num}</div>'
             f'<div class="fr-l z">{"".join(ficha(f, "fx fx-h") for f in fs)}</div>')
    return pagina(x, "L-fichas-grade", inner, "n1")

def L_fichas_prateleira(x):
    g = fichas(x["corpo"]); fs = [f for _, L in g for f in L]
    cab, num = cat_cab(x, int(x["mk"].get("numero", ["0"])[0]), " · página 1 de 2")
    potes = "".join(f'<li><div class="fp-img">{pk_img(f)}</div></li>' for f in fs)
    textos = "".join(f'<li><div class="fx-img fp-mini">{pk_img(f)}</div><div class="fp-tt"><header class="fx-cab"><b class="fx-n">{esc(f["nome"])}</b><span class="fx-esp">{esc(f["esp"])}</span>{selos(f)}</header>{fx_cbv(f)}</div></li>' for f in fs)
    inner = (f'<div class="fp-cab z"><div>{cab}</div>{num}</div>'
             f'<ul class="fp-potes z">{potes}</ul><div class="fp-tabua z" aria-hidden="true"></div><ul class="fp-txt z">{textos}</ul>')
    return pagina(x, "L-fichas-prateleira", inner)

def L_fichas_tabela(x):
    mk = x["mk"]; g = fichas(x["corpo"]); fs = [f for _, L in g for f in L]
    cab, _ = cat_cab(x, 0)
    th = "".join(f'<th scope="col"><span class="tb-l tb-{k}">{L}</span>{t}</th>' for k, L, t in CBV3)
    linhas = "".join(f'<tr><th scope="row"><div class="tb-p">{pk_img(f)}<div><b class="fx-n">{esc(f["nome"])}</b><span class="fx-esp">{esc(f["esp"])}</span>{selos(f)}</div></div></th>'
                     + "".join(f'<td>{inl(f[k])}</td>' for k, _, _ in CBV3) + "</tr>" for f in fs)
    inner = (f'<div class="tb-q z"><span class="tb-pg">Suplementos · página 2 de 2</span>{cab}'
             f'<table class="tb-t"><thead><tr><th scope="col">Produto</th>{th}</tr></thead><tbody>{linhas}</tbody></table>{linha_extra(mk)}</div>'
             f'<figure class="tb-f z zf">{ft(mk["foto"][0], "ft", "50% 60%", "Cão idoso de focinho grisalho")}{legenda(mk, x["n"], x["k"], "leg sobre")}</figure>')
    return pagina(x, "L-fichas-tabela", inner, sem_rh=True)

def L_fichas_bula(x):
    mk = x["mk"]; g = fichas(x["corpo"])
    n_tot = sum(len(L) for _, L in g)
    cols = "".join(f'<section class="bu-col"><h3><span>{i + 1}</span>{esc(nome)}</h3>'
                   + "".join(ficha(f, "fx fx-bu") for f in L) + "</section>" for i, (nome, L) in enumerate(g))
    inner = (f'<div class="bu-cab z">{kick("categoria")}{h2(x["titulo"])}<p class="lead">{inl(mk["lead"][0])}</p></div>'
             f'<div class="bu-selo z" aria-hidden="true"><span>uso com orientação do</span><b>veterinário</b><span>medicamentos · 10 produtos</span></div>'
             f'<div class="bu-cols z">{cols}</div>')
    return pagina(x, "L-fichas-bula", inner)

def L_fichas_quadro(x):
    mk = x["mk"]; g = fichas(x["corpo"])
    blocos = "".join(f'<section class="qd-g"><h3>{esc(nome)}</h3><div class="qd-l">{"".join(ficha(f, "fx fx-qd") for f in L)}</div></section>' for nome, L in g)
    regras = "".join(f'<li><span>{i + 1}</span>{inl(r)}</li>' for i, r in enumerate(mk.get("regra", [])))
    inner = (f'<div class="qd-cab z">{kick("categoria")}{h2(x["titulo"])}</div><div class="qd-q z">{blocos}</div>'
             f'<aside class="qd-ps z"><b class="qd-pt">No balcão, com receita</b><ol>{regras}</ol>{linha_extra(mk, "qd-linha")}'
             f'<span class="qd-pg">Medicamentos · página 2 de 2</span></aside>')
    return pagina(x, "L-fichas-quadro", inner, "navy")

def L_fichas_ritual(x):
    mk = x["mk"]; g = fichas(x["corpo"]); fs = [f for _, L in g for f in L]
    bris = [f for f in fs if f["pk"].startswith("bris")]; ouv = [f for f in fs if not f["pk"].startswith("bris")]
    passos = ("no banho", "depois do banho", "para finalizar")
    br = "".join(f'<li><span class="ri-n">{i + 1}<small>{passos[i]}</small></span>{ficha(f, "fx fx-rt")}</li>' for i, f in enumerate(bris))
    ou = "".join(ficha(f, "fx fx-h fx-ou") for f in ouv)
    cab, num = cat_cab(x, len(fs))
    inner = (f'<figure class="ri-f z zf">{ft(mk["foto"][0], "ft", "50% 70%", "Gato enrolado na toalha depois do banho")}{legenda(mk, x["n"], x["k"], "leg sobre")}</figure>'
             f'<div class="ri-q z"><div class="ri-cab"><div>{cab}</div>{num}</div>'
             f'<h3 class="ri-sub">Pele e pelos: a linha Bris em três passos</h3><ol class="ri-l">{br}</ol>'
             f'<h3 class="ri-sub">Ouvidos</h3><div class="ri-ou">{ou}</div></div>')
    return pagina(x, "L-fichas-ritual", inner, sem_rh=True)

def L_fichas_dupla(x):
    mk = x["mk"]; g = fichas(x["corpo"]); fs = [f for _, L in g for f in L]
    cab, num = cat_cab(x, len(fs))
    inner = (f'<figure class="du-f z zf">{ft(mk["foto"][0], "ft", "50% 65%", "Filhote deitado no piso limpo")}{legenda(mk, x["n"], x["k"], "leg sobre")}</figure>'
             f'<div class="du-q z"><div class="du-cab"><div>{cab}</div>{num}</div>'
             f'<div class="du-l">{"".join(ficha(f, "fx fx-du", rotulo=True) for f in fs)}</div>{nota_sf(mk, "sf-nota du-sf")}</div>')
    return pagina(x, "L-fichas-dupla", inner, sem_rh=True)

LAYOUTS = {k[2:]: v for k, v in globals().items() if k.startswith("L_")}

# ------------------------------------------------------------------ montagem
ORDEM = [f"cap{n:02d}.md" for n in range(ULT + 1)] + ["fechamento.md"]

def ler():
    caps = []
    for a in ORDEM:
        meta, body = B.front(open(os.path.join(C, a), encoding="utf-8").read())
        meta["n"] = int(meta["cap"]); meta["body"] = body; caps.append(meta); CAPS[meta["n"]] = meta
    return caps

def capitulo(m):
    n = m["n"]; out = []
    lista = []
    for tipo, tit, linhas in B.slides_do(m["body"]):
        if tipo == "validar":
            if lista: lista[-1][3].append(" ".join(l.strip() for l in linhas if l.strip()))
            continue
        lista.append([tipo, tit, linhas, []])
    if n == 0: out.append(prefacio(m))
    elif m.get("capa") != "nao":
        out.append(capa_cap(m, [(f"cap{n:02d}-{k}", it[1]) for k, it in enumerate(lista, 1)]))
    for k, (tipo, tit, linhas, notas) in enumerate(lista, 1):
        mk, corpo = B.separa(linhas)
        sid = f"cap{n:02d}" if (k == 1 and m.get("capa") == "nao") else f"cap{n:02d}-{k}"
        x = dict(n=n, k=k, tipo=tipo, titulo=tit, mk=mk, corpo=corpo, notas=notas, sid=sid, linhas=linhas)
        lay = (mk.get("layout") or [""])[0]
        if lay in ("checklist", "quiz"): out.append(L_reuso(x, lay))
        elif lay in LAYOUTS: out.append(LAYOUTS[lay](x))
        else: raise SystemExit(f"layout desconhecido: {lay} em cap{n} slide {k}")
    if n == 0: out.append(sumario())
    return "".join(out)

def montar():
    prepara_fotos()
    caps = ler()
    corpo = capa_guia() + "".join(capitulo(m) for m in caps)
    ids = re.findall(r'<section class="slide[^"]*"[^>]*?id="([^"]+)"', corpo)
    corpo = re.sub(r"\{\{PG:([\w-]+)\}\}", lambda x: str(ids.index(x.group(1)) + 1) if x.group(1) in ids else "", corpo)
    k = [0]
    def par(mm):
        k[0] += 1; return mm.group(0).replace('class="slide ', f'class="slide {"pg-par" if k[0] % 2 == 0 else "pg-impar"} ', 1)
    corpo = re.sub(r'<section class="slide [^"]*"', par, corpo)
    nval = corpo.count('class="validar"')
    css = (open(os.path.join(ROOT, "tools/deck/estrutura.css"), encoding="utf-8").read() + CSS_ICONES
           + open(os.path.join(ROOT, "tools/deck/visual.css"), encoding="utf-8").read()
           + open(os.path.join(AQUI, "livro.css"), encoding="utf-8").read())
    js = open(os.path.join(ROOT, "tools/deck/deck.js"), encoding="utf-8").read()
    indice = "".join(f'<li><a href="#cap{m["n"]:02d}" data-cap="{m["n"]:02d}"><span>{m["n"] if 1 <= m["n"] <= ULT else ""}</span>{inl(m["titulo"])}</a></li>' for m in caps)
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Guia de Execução no PDV · Ourofino Pet</title>
<meta name="description" content="Guia de execução no ponto de venda da Ourofino Pet, para promotores, vendedores do distribuidor e equipes de loja.">
<meta name="theme-color" content="#072047">
<link rel="icon" href="assets/marca/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Young+Serif&family=Poppins:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500&family=Caveat:wght@600;700&display=swap" rel="stylesheet">
<style>{css}</style>
</head>
<body>
<div class="rolo"><main class="palco">
{corpo}
</main></div>
<div class="prog"><i></i></div>
<nav class="nav" aria-label="Navegação do guia">
<img class="nav-logo" src="assets/marca/logo-negativo.svg" alt="Ourofino" width="130" height="22">
<button type="button" data-abre-indice title="Índice">{icone("checklist", "nav-ic")}<span class="nav-r">Índice</span></button>
<span class="nav-cap" data-cap-txt></span>
<button type="button" data-rev aria-pressed="false" title="Mostrar as {nval} notas para a Ourofino validar"><span class="nav-r">Revisão</span><span class="nav-c">R</span></button>
<button type="button" data-pdf title="Baixar PDF"><span class="nav-r">PDF</span><span class="nav-c">PDF</span></button>
<span class="nav-cont" data-cont></span>
<button type="button" class="seta-bt" data-ant aria-label="Slide anterior">{icone("seta", "seta-v")}</button>
<button type="button" class="seta-bt" data-prox aria-label="Próximo slide">{icone("seta")}</button>
</nav>
<div class="indice" id="indice" hidden><div class="fecha-fundo" data-fecha></div><div class="indice-painel"><button type="button" class="ind-x" data-fecha aria-label="Fechar">×</button>
<h3>Índice</h3><ol>{indice}</ol><a class="ind-tr" href="#sumario">Sumário com as páginas</a></div></div>
<script>{js}</script>
</body>
</html>"""

if __name__ == "__main__":
    out = montar()
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(out)
    print("index.html", len(out) // 1024, "KB", out.count('<section class="slide'), "slides")
