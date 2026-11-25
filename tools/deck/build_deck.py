"""Gera o deck de slides do guia (v4) a partir de conteudo-v4/*.md.
Rodar da raiz: python3 tools/deck/build_deck.py  ->  index.html"""
import html, json, os, re, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, AQUI); sys.path.insert(0, os.path.dirname(AQUI))
from icones import icone, I as ICONES, CSS as CSS_ICONES
import diagramas as DG
import build as V3  # reaproveita mapa de imagens, marcações e utilidades da v3

C = os.environ.get("CONTEUDO_V4", os.path.join(ROOT, "conteudo-v4")); IMG = "assets/img/"; FOTO = "assets/img/foto/"
esc = lambda s: html.escape(s or "", quote=True)

# ------------------------------------------------------------------ leitura
def front(txt):
    m = re.match(r"^---\n(.*?)\n---\n", txt, re.S)
    meta, key = {}, None
    for line in m.group(1).split("\n"):
        if re.match(r"^\s+- ", line) and key: meta[key].append(line.strip()[2:].strip())
        elif ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1); key = k.strip(); v = v.strip()
            if len(v) > 1 and v[0] == v[-1] and v[0] in "\"'": v = v[1:-1]
            meta[key] = v if v else []
    return meta, txt[m.end():]

def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r'"([^"\n]+)"', "“\\1”", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
    s = re.sub(r"\b([Cc]apítulos?) (\d{1,2})\b", lambda m: f'<a class="xref" href="#cap{int(m.group(2)):02d}">{m.group(0)}</a>', s)
    return s

def slides_do(body):
    """divide o corpo em slides: [(tipo, titulo, linhas)]"""
    out = []; atual = None
    for l in body.split("\n"):
        m = re.match(r"^===\s*([\w-]+)\s*(?:\|\s*(.*))?$", l.strip())
        if m:
            atual = [m.group(1).lower(), (m.group(2) or "").strip(), []]; out.append(atual); continue
        if atual is not None: atual[2].append(l)
    return out

def separa(linhas):
    """marcadores @ e corpo"""
    mk = {}; corpo = []
    for l in linhas:
        m = re.match(r"^@([\w-]+)\s*(.*)$", l.strip())
        if m: mk.setdefault(m.group(1), []).append(m.group(2).strip()); continue
        corpo.append(l)
    while corpo and not corpo[-1].strip(): corpo.pop()
    while corpo and not corpo[0].strip(): corpo.pop(0)
    return mk, corpo

def paragrafos(corpo):
    blocos = []; buf = []
    for l in corpo:
        if not l.strip():
            if buf: blocos.append(" ".join(buf)); buf = []
        else: buf.append(l.strip())
    if buf: blocos.append(" ".join(buf))
    return blocos

def md(corpo):
    """markdown simples: parágrafos, listas, tabelas"""
    out = []; i = 0; L = corpo
    while i < len(L):
        l = L[i].strip()
        if not l: i += 1; continue
        if l.startswith("|"):
            rows = []
            while i < len(L) and L[i].strip().startswith("|"): rows.append(L[i].strip()); i += 1
            out.append(tabela(rows)); continue
        if re.match(r"^[-*] ", l):
            it = []
            while i < len(L) and re.match(r"^[-*] ", L[i].strip()): it.append(L[i].strip()[2:]); i += 1
            out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in it) + "</ul>"); continue
        if re.match(r"^\d+\. ", l):
            it = []
            while i < len(L) and re.match(r"^\d+\. ", L[i].strip()): it.append(re.sub(r"^\d+\.\s*", "", L[i].strip())); i += 1
            out.append("<ol>" + "".join(f"<li>{inline(x)}</li>" for x in it) + "</ol>"); continue
        # cada linha é um parágrafo (os redatores escrevem um parágrafo por linha)
        out.append(f"<p>{inline(l)}</p>"); i += 1
    return "".join(out)

def tabela(rows):
    rows = [[c.strip() for c in r.strip("|").split("|")] for r in rows if not re.match(r"^\|[\s:|-]+\|$", r)]
    cab, corpo = rows[0], rows[1:]
    th = "".join(f"<th>{inline(c)}</th>" for c in cab)
    trs = "".join("<tr>" + "".join(f'<td data-l="{esc(re.sub(r"[*]", "", cab[k]))}">{inline(c)}</td>' for k, c in enumerate(r)) + "</tr>" for r in corpo)
    return f'<table class="tab"><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>'

# ------------------------------------------------------------------ imagens
def img_fig(fid, alt="", cls="", sizes="(min-width: 760px) 60vw, 100vw"):
    nome = V3.fonte(fid); w, h = V3.dims_nome(nome); base = IMG + nome
    if fid.startswith("P-"):
        return f'<img class="{cls}" src="{base}.webp" width="{w}" height="{h}" alt="{esc(alt)}" loading="lazy" decoding="async">'
    srcset = f'{base}-900.webp 900w, {base}.webp {w}w' if os.path.exists(os.path.join(ROOT, base + "-900.webp")) else f"{base}.webp {w}w"
    return f'<img class="{cls}" src="{base}.webp" srcset="{srcset}" sizes="{sizes}" width="{w}" height="{h}" alt="{esc(alt)}" loading="lazy" decoding="async">'

def recorte(nome, cls="", alt="", pasta=IMG):
    f = os.path.join(ROOT, pasta + nome + ".webp")
    if not os.path.exists(f): return ""
    from PIL import Image
    w, h = Image.open(f).size
    return f'<img class="{cls}" src="{pasta}{nome}.webp" width="{w}" height="{h}" alt="{esc(alt)}" loading="lazy" decoding="async">'

def foto(nome, cls="", alt=""):
    f = os.path.join(ROOT, FOTO + nome + ".webp")
    if not os.path.exists(f): return ""
    from PIL import Image
    w, h = Image.open(f).size
    ss = f' srcset="{FOTO}{nome}-900.webp 900w, {FOTO}{nome}.webp {w}w" sizes="100vw"' if os.path.exists(os.path.join(ROOT, FOTO + nome + "-900.webp")) else ""
    return f'<img class="{cls}" src="{FOTO}{nome}.webp"{ss} width="{w}" height="{h}" alt="{esc(alt)}" loading="lazy" decoding="async">'

def serafina(pose, cls="sera"):
    return recorte("serafina-" + (pose or "explica"), cls, "Serafina")

def diagrama(fid):
    s = DG.DIAGRAMAS[fid]()
    return s.replace("Figtree, sans-serif", "Poppins, sans-serif").replace("IBM Plex Mono, monospace", "Poppins, sans-serif")

ILU = {"I-CHEGADA": "cena-chegada-sem-fundo", "I-CONVERSA": "cena-conversa-sem-fundo", "I-TUTOR": "cena-tutor-sem-fundo"}

PARES = {("F-ANTES", "F-DEPOIS"): ("Antes", "Depois"), ("F-PONTO-EXTRA-ERRADO", "F-PONTO-EXTRA-CERTO"): ("Errado", "Certo")}

def visual_fig(fids, legenda=""):
    fids = [f.split()[0] for f in fids if f.strip()]
    if len(fids) == 2 and (fids[0], fids[1]) in PARES or len(fids) == 2 and (fids[1], fids[0]) in PARES:
        a, b = fids if (fids[0], fids[1]) in PARES else (fids[1], fids[0]); ta, tb = PARES[(a, b)]
        return (f'<div class="comp" data-comp><div class="comp-quadro"><div class="comp-b">{img_fig(b)}<div class="rot">{V3.rotulos(b)}</div></div>'
                f'<div class="comp-a">{img_fig(a)}<div class="rot">{V3.rotulos(a)}</div></div><span class="comp-tag a">{ta}</span><span class="comp-tag b">{tb}</span>'
                f'<div class="comp-linha"><span>{icone("seta")}</span></div><input class="comp-range" type="range" min="0" max="100" value="50" aria-label="Arraste para comparar"></div></div>')
    out = []
    for fid in fids:
        if fid in ILU: out.append(recorte(ILU[fid], "ilu", legenda))
        elif fid.startswith("D-") and fid in DG.DIAGRAMAS: out.append(f'<div class="dg-caixa">{diagrama(fid)}</div>')
        elif fid.startswith("P-"): out.append(f'<div class="prod">{img_fig(fid, legenda)}</div>')
        else:
            rot = V3.rotulos(fid)
            out.append(f'<div class="foto-q">{img_fig(fid, legenda)}{f"<div class=rot>{rot}</div><button class=rot-btn type=button>Ocultar marcações</button>" if rot else ""}</div>')
    return "".join(out)

def tipo_fig(fids):
    f = fids[0].split()[0] if fids else ""
    if f in ILU: return "ilu"
    if f.startswith("D-"): return "dg"
    if f.startswith("P-"): return "prod"
    w, h = V3.dims(f) if f else (3, 2)
    return "retrato" if h > w * 1.05 else "paisagem"

# ------------------------------------------------------------------ capas de capítulo (uma diferente por capítulo)
CAPAS = {
    0:  dict(v="serafina", cor="navy", img="serafina-acena", animais=True),
    1:  dict(v="recorte", cor="verde", img="estudio-cao-viralata-caramelo"),
    2:  dict(v="tipografica", cor="n1", img="estudio-cao-dachshund"),
    3:  dict(v="lateral", lado="dir", cor="navy", img="cor-cao-golden-azul", pos="50% 30%"),
    4:  dict(v="espiando", cor="azul", img="estudio-gato-laranja"),
    5:  dict(v="lateral", lado="esq", cor="branco", img="cor-cao-bulldog-frances-verde", pos="50% 45%"),
    6:  dict(v="dupla", img="estudio-cao-e-gato-02", img2="estudio-gato-frajola-filhote"),
    7:  dict(v="lateral", lado="dir", cor="azul", img="cor-cao-jack-russell-rosa", pos="50% 62%"),
    8:  dict(v="folha", cor="branco", img="cena-tutora-cao-casa", pos="50% 35%"),
    9:  dict(v="lateral", lado="esq", cor="navy", img="cor-cao-border-collie-laranja", pos="50% 55%"),
    10: dict(v="folha", cor="n1", img="ambiente-petshop-balcao-gato", pos="40% 50%"),
    11: dict(v="lateral", lado="dir", cor="verde", img="cor-cao-preto-amarelo", pos="50% 35%"),
    12: dict(v="geometrica", cor="navy", img="estudio-cao-beagle"),
    13: dict(v="lateral", lado="dir", cor="navy", img="cor-gato-cinza-amarelo", pos="62% 50%"),
    14: dict(v="serafina", cor="branco", img="serafina-acena", pet="estudio-filhote-bernese"),
    97: dict(v="tipografica", cor="branco", img="estudio-cao-shih-tzu"),
    98: dict(v="recorte", cor="azul", img="serafina-tablet", sera=True),
    99: dict(v="sangrada", img="cor-gato-frajola-rosa", pos="40% 50%"),
}

def animais_geo(cls="geo", arq="animais-faixa"):
    g = open(os.path.join(ROOT, f"assets/marca/elementos/{arq}.svg")).read()
    return f'<div class="{cls}" aria-hidden="true">{g}</div>'

def capa_cap(m):
    n = m["n"]; c = CAPAS.get(n, dict(v="recorte", cor="navy", img="estudio-cao-beagle")); v = c["v"]
    num = f'<span class="cc-num">{n:02d}</span>' if n < 97 else ""
    manus = f'<span class="cc-manus">{esc(m.get("manuscrito", ""))}</span>' if m.get("manuscrito") else ""
    kicker = f'<span class="cc-parte">{"Capítulo " + str(n) + " · " if n < 97 else ""}{esc(m.get("parte", ""))}</span>'
    tam = "" if c.get("v") != "tipografica" else ' style="font-size:%dpx"' % (150 if len(m["titulo"]) <= 18 else 118 if len(m["titulo"]) <= 30 else 96)
    tit = f'<h2 class="cc-tit"{tam}>{inline(m["titulo"])}</h2>'
    abre = f'<p class="cc-abre">{inline(m.get("abertura", ""))}</p>' if m.get("abertura") else ""
    txt = f'<div class="cc-txt" data-e style="--e:1">{num}{kicker}{manus}{tit}{abre}</div>'
    if v == "sangrada":
        vis = f'<div class="cc-foto" style="--pos:{c.get("pos", "50% 50%")}">{foto(c["img"], "cc-img")}</div>'
    elif v == "lateral":
        vis = f'<div class="cc-lat" style="--pos:{c.get("pos", "50% 50%")}">{foto(c["img"], "cc-img")}</div>'
    elif v in ("recorte", "espiando", "tipografica"):
        src = recorte(c["img"], "cc-pet", "", IMG) if c.get("sera") else recorte(c["img"], "cc-pet", "", FOTO)
        vis = f'<div class="cc-pet-q">{src}</div>'
    elif v == "folha":
        vis = f'<div class="cc-folha" style="--pos:{c.get("pos", "50% 50%")}">{foto(c["img"], "cc-img")}</div>'
    elif v == "dupla":
        vis = (f'<div class="cc-dupla"><div class="cc-lado a">{recorte(c["img"], "cc-pet", "", FOTO)}</div>'
               f'<div class="cc-lado b">{recorte(c["img2"], "cc-pet", "", FOTO)}</div></div>')
    elif v == "geometrica":
        vis = f'{animais_geo("geo cc-geo")}<div class="cc-pet-q">{recorte(c["img"], "cc-pet", "", FOTO)}</div>'
    elif v == "serafina":
        pet = f'<div class="cc-pet2">{recorte(c["pet"], "cc-pet", "", FOTO)}</div>' if c.get("pet") else ""
        geo = animais_geo("geo cc-geo") if c.get("animais") else ""
        vis = f'{geo}<div class="cc-sera">{serafina("acena", "cc-sera-img")}</div>{pet}'
    else: vis = ""
    return (f'<section class="slide capa-cap v-{v} cor-{c.get("cor", "navy")}" data-lado="{c.get("lado", "")}" id="cap{n:02d}" data-cap="{n:02d}" data-cap-nome="{esc(cap_nome(m))}">'
            f'{vis}{txt}</section>')

def cap_nome(m):
    return (f'{m["n"]}. ' if m["n"] < 97 else "") + m["titulo"]

# ------------------------------------------------------------------ slides de conteúdo
def cab(m, k, tot):
    return (f'<header class="cab"><span class="cab-n">{m["n"] if m["n"] < 97 else ""}</span><span class="cab-t">{esc(m["titulo"])}</span></header>'
            f'<footer class="pe"><span>Guia de execução no PDV</span><span class="pe-n" data-pagina></span></footer>')

def validar_html(notas):
    return "".join(f'<aside class="validar"><b>Para a Ourofino validar</b><p>{inline(n)}</p></aside>' for n in notas)

def lembre_html(mk):
    return f'<p class="lembre"><b>Lembre-se.</b> {inline(mk["lembre"][0])}</p>' if mk.get("lembre") else ""

def icones_html(mk, cls="ic-g"):
    out = ""
    for k, nome in enumerate(mk.get("icone", [])):
        nome = nome.split()[0]
        if nome in ICONES: out += f'<span class="{cls}" style="--d:{k * 0.15}">{icone(nome)}</span>'
    return out

TESTE_N = [0]; POSES = ["explica", "aponta", "joinha", "acena"]; POSE_I = [0]

def slide(m, k, tipo, titulo, linhas, notas):
    mk, corpo = separa(linhas); n = m["n"]
    sid = f"cap{n:02d}-{k}"; attrs = f'class="slide s-{tipo}" id="{sid}" data-cap="{n:02d}" data-cap-nome="{esc(cap_nome(m))}"'
    T = f'<h3 class="tit" data-e>{inline(titulo)}</h3>' if titulo else ""
    figs = mk.get("fig", []); val = validar_html(notas); lem = lembre_html(mk); chrome = cab(m, k, 0)
    pratica = f'<div class="pratica" data-e style="--e:3"><b>Na prática</b><p>{inline(mk["na-pratica"][0])}</p></div>' if mk.get("na-pratica") else ""
    exemplo = f'<div class="pratica" data-e style="--e:3"><b>Exemplo</b><p>{inline(mk["exemplo"][0])}</p></div>' if mk.get("exemplo") else ""

    if tipo in ("conceito", "porque", "figura"):
        texto = f'<div class="txt" data-e style="--e:1">{md(corpo)}</div>'
        if tipo == "porque" and mk.get("dado"):
            dado = mk["dado"][0]
            mnum = None
            for padrao in (r"(R\$\s?[\d.,]+(?:\s(?:mil|milhão|milhões|bilhão|bilhões))?)", r"(\d+(?:[.,]\d+)?\s?%)",
                           r"(\d+(?:[.,]\d+)?\s(?:mil|milhão|milhões|bilhão|bilhões))", r"(?<![\d/])((?!(?:19|20)\d\d\b)\d+(?:[.,]\d+)?)(?![\d/])"):
                mnum = re.search(padrao, dado)
                if mnum: break
            tam = ' style="font-size:%dpx"' % (210 if len(mnum.group(1)) <= 5 else 150 if len(mnum.group(1)) <= 9 else 110) if mnum else ""
            grande = (f'<span class="dado-n"{tam}>{esc(mnum.group(1))}</span><span class="dado-t">{inline(dado)}</span>' if mnum
                      else f'<span class="dado-t so">{inline(dado)}</span>')
            fonte = f'<p class="fonte">Fonte: {inline(mk["fonte"][0])}</p>' if mk.get("fonte") else ""
            return (f'<section {attrs}>{chrome}<div class="dado" data-e>{grande}{fonte}</div><div class="col-txt" data-fit>{T}{texto}{pratica}</div>{lem}'
                    f'{icones_html(mk, "ic-canto")}{val}</section>')
        if figs:
            tf = tipo_fig(figs)
            vis = visual_fig(figs, titulo)
            return f'<section {attrs} data-fig="{tf}">{chrome}<div class="col-txt" data-fit>{T}{texto}{pratica}{exemplo}</div><div class="col-vis" data-e style="--e:2">{vis}</div>{lem}{icones_html(mk, "ic-canto")}{val}</section>'
        if mk.get("pose"):
            return f'<section {attrs} data-vis="sera">{chrome}<div class="col-txt" data-fit>{T}{texto}{pratica}{exemplo}</div><div class="col-vis">{serafina(mk["pose"][0])}</div>{lem}{val}</section>'
        ic = icones_html(mk, "ic-grande") or f'<span class="ic-grande">{icone("folha")}</span>'
        palavras = len(" ".join(corpo).split()) + len((mk.get("na-pratica") or mk.get("exemplo") or [""])[0].split())
        if palavras > 95: attrs += ' data-largo="1"'
        return f'<section {attrs} data-vis="icone">{chrome}<div class="col-txt" data-fit>{T}{texto}{pratica}{exemplo}</div><div class="col-vis">{ic}</div>{lem}{val}</section>'

    if tipo == "termo":
        return (f'<section {attrs}>{chrome}<div class="termo-q" data-fit><span class="termo-r">o que é</span><h3 class="termo-p" data-e>{inline(titulo)}</h3>'
                f'<div class="termo-def" data-e style="--e:1">{md(corpo)}</div>{exemplo}{pratica}</div>{icones_html(mk, "ic-canto")}{lem}{val}</section>')

    if tipo == "passos":
        it = []
        for l in corpo:
            l = re.sub(r"^\d+\.\s*", "", l.strip())
            if not l: continue
            mm = re.match(r"\*\*(.+?)\*\*\s*·\s*(.*)", l)
            it.append((mm.group(1), mm.group(2)) if mm else ("", l))
        ics = [x.split()[0] for x in mk.get("icone", [])]
        lis = "".join(f'<li data-e style="--e:{i + 1}"><span class="p-n">{i + 1}</span>{f"<span class=p-ic style=--d:{i * .2}>{icone(ics[i])}</span>" if i < len(ics) and ics[i] in ICONES else ""}'
                      f'<b>{inline(t)}</b><span class="p-t">{inline(d)}</span></li>' for i, (t, d) in enumerate(it))
        return f'<section {attrs} data-n="{len(it)}">{chrome}{T}<ol class="passos">{lis}</ol>{pratica}{lem}{val}</section>'

    if tipo == "comparar":
        bons = [inline(l.strip()[1:].strip()) for l in corpo if l.strip().startswith("+")]
        maus = [inline(l.strip()[1:].strip()) for l in corpo if l.strip().startswith("-")]
        vis = f'<div class="cmp-fig">{visual_fig(figs)}</div>' if figs else ""
        return (f'<section {attrs}>{chrome}{T}<div class="cmp"><div class="cmp-l mau" data-e style="--e:1"><h4>{icone("errado")}Evite</h4><ul>{"".join(f"<li>{x}</li>" for x in maus)}</ul></div>'
                f'<div class="cmp-l bom" data-e style="--e:2"><h4>{icone("certo")}Faça</h4><ul>{"".join(f"<li>{x}</li>" for x in bons)}</ul></div></div>{vis}{lem}{val}</section>')

    if tipo == "erro":
        j = " ".join(l.strip() for l in corpo)
        mm = re.match(r"\*\*O que acontece:\*\*(.*?)\*\*Faça assim:\*\*(.*)", j, re.S)
        a, b = (mm.group(1).strip(), mm.group(2).strip()) if mm else (j, "")
        cap1 = lambda t: t[:1].upper() + t[1:] if t else t
        return (f'<section {attrs}>{chrome}<div class="err-sera">{serafina("atencao")}</div><div class="err-txt" data-fit><span class="err-r">Erro comum</span>{T}'
                f'<div class="err-a" data-e style="--e:1"><b>O que acontece</b><p>{inline(cap1(a))}</p></div>'
                f'<div class="err-b" data-e style="--e:2"><b>Faça assim</b><p>{inline(cap1(b))}</p></div></div>{lem}{val}</section>')

    if tipo == "serafina":
        pose = (mk.get("pose") or [POSES[POSE_I[0] % 4]])[0]; POSE_I[0] += 1
        lado = "dir" if POSE_I[0] % 2 else "esq"; fundo = ["branco", "n1", "verde", "azul"][(POSE_I[0] // 2) % 4]
        return (f'<section {attrs} data-lado="{lado}" data-fundo="{fundo}">{chrome}<div class="sf-img">{serafina(pose)}</div><div class="sf-fala" data-e data-fit><span class="sf-nome">Serafina</span>'
                f'{T}<div class="sf-txt">{md(corpo)}</div></div>{lem}{val}</section>')

    if tipo == "cards":
        cs = []
        ics = [x.split()[0] for x in mk.get("icone", [])]
        for l in corpo:
            mm = re.match(r"\*\*(.+?)\*\*\s*·\s*(.*)", l.strip())
            if mm: cs.append((mm.group(1), mm.group(2)))
        lis = "".join(f'<li data-e style="--e:{i + 1}">{f"<span class=c-ic style=--d:{i * .15}>{icone(ics[i])}</span>" if i < len(ics) and ics[i] in ICONES else ""}<b>{inline(t)}</b><p>{inline(d)}</p></li>' for i, (t, d) in enumerate(cs))
        vis = f'<div class="cards-fig">{visual_fig(figs, titulo)}</div>' if figs else ""
        return f'<section {attrs} data-n="{len(cs)}"{" data-fig=1" if figs else ""}>{chrome}{T}<ul class="cards">{lis}</ul>{vis}{lem}{val}</section>'

    if tipo == "tabela":
        return f'<section {attrs}>{chrome}{T}<div class="tab-q" data-e style="--e:1">{md(corpo)}</div>{lem}{val}</section>'

    if tipo == "conversa":
        falas = []
        for l in corpo:
            if ":" not in l: continue
            q, _, f = l.partition(":"); qq = q.strip().lower()
            lado = "eu" if qq in ("você", "voce", "promotor", "promotora", "serafina") else "outro"
            falas.append(f'<div class="fala {lado}" data-e style="--e:{len(falas) + 1}"><span>{esc(q.strip())}</span><p>{inline(f.strip())}</p></div>')
        return f'<section {attrs}>{chrome}<div class="cv-sera">{serafina("tablet")}</div><div class="cv-q" data-fit>{T}<div class="conversa">{"".join(falas)}</div></div>{lem}{val}</section>'

    if tipo == "teste":
        q = titulo; ops = []; exp = []
        for l in corpo:
            s = l.strip()
            if s.startswith("?"): q = s[1:].strip()
            elif s.startswith("- [x]"): ops.append((True, s[5:].strip()))
            elif s.startswith("- [ ]"): ops.append((False, s[5:].strip()))
            elif s.startswith(">"): exp.append(s[1:].strip())
        bts = "".join(f'<button type="button" class="op" data-ok="{1 if ok else 0}"><span class="op-l">{chr(65 + i)}</span><span>{inline(o)}</span></button>' for i, (ok, o) in enumerate(ops))
        return (f'<section {attrs}>{chrome}<div class="ts-q" data-fit><span class="ts-r">Teste rápido</span><p class="ts-p">{inline(q)}</p><div class="ops" data-teste>{bts}'
                f'<div class="teste-exp" hidden><b class="teste-res"></b> {inline(" ".join(exp))}</div></div></div><div class="ts-sera">{serafina("pensa")}</div>{val}</section>')

    if tipo == "resumo":
        it = [re.sub(r"^[-*]\s*", "", l.strip()) for l in corpo if l.strip()]
        pet = CAPAS.get(n, {}).get("img", "")
        RECORTES = ["estudio-cao-lulu-pomeranian", "estudio-filhote-labrador", "estudio-cao-shih-tzu", "estudio-gato-branco",
                    "estudio-filhote-viralata-caramelo", "estudio-cao-bulldog-frances", "estudio-gato-frajola-filhote", "estudio-filhote-bernese"]
        if not pet.startswith("estudio"): pet = RECORTES[n % len(RECORTES)]
        petimg = recorte(pet, "rs-pet", "", FOTO)
        return (f'<section {attrs}>{chrome}<div class="rs-q" data-fit><h3 class="tit">{inline(titulo or "Para levar")}</h3><ul class="rs">'
                + "".join(f'<li data-e style="--e:{i + 1}"><span style="--d:{i * .2}">{icone("certo")}</span>{inline(x)}</li>' for i, x in enumerate(it))
                + f'</ul></div><div class="rs-img">{petimg}</div>{val}</section>')

    return f'<section {attrs}>{chrome}{T}<div class="txt">{md(corpo)}</div>{val}</section>'

# ------------------------------------------------------------------ apêndices (formato da v3)
def checklist(m):
    secs = re.split(r"^## ", m["body"], flags=re.M)[1:]; out = []; kk = 0
    for k, s in enumerate(secs):
        tit, _, resto = s.partition("\n")
        itens = [re.sub(r"^- \[[ x]\]\s*", "", l.strip()) for l in resto.split("\n") if l.strip().startswith("- [")]
        lis = ""
        for x in itens:
            kk += 1; lis += f'<label class="chk"><input type="checkbox" data-k="c{kk}"><span class="chk-box">{icone("certo")}</span><span>{inline(x)}</span></label>'
        out.append(f'<section class="slide s-check" id="cap98-{k + 1}" data-cap="98" data-cap-nome="Checklist da visita">{cab(m, k, 0)}<div class="ck-cab"><h3 class="tit">{inline(tit.strip())}</h3>'
                   f'<p class="ck-prog"><span data-chk-txt></span> marcados <i><b data-chk-barra></b></i><button type="button" data-limpar>Limpar</button></p></div><div class="ck-lista" data-n="{len(itens)}">{lis}</div></section>')
    return "".join(out)

def glossario(m):
    itens = []
    for l in m["body"].split("\n"):
        mm = re.match(r"\*\*(.+?)\*\*\s*·\s*(.*)", l.strip())
        if mm:
            t, d = mm.group(1), mm.group(2); ex = ""
            if "Exemplo:" in d: d, ex = d.split("Exemplo:", 1)
            itens.append((t, d.strip(), ex.strip()))
    out = []; por = 8
    for p in range(0, len(itens), por):
        grupo = itens[p:p + por]; ini, fim = grupo[0][0][0].upper(), grupo[-1][0][0].upper()
        dl = "".join(f'<div class="g-item"><dt>{esc(t)}</dt><dd>{inline(d)}{f"<span class=g-ex>Exemplo: {inline(e)}</span>" if e else ""}</dd></div>' for t, d, e in grupo)
        out.append(f'<section class="slide s-gloss" id="cap97-{p // por + 1}" data-cap="97" data-cap-nome="Glossário">{cab(m, 0, 0)}<h3 class="tit">{ini}{" a " + fim if fim != ini else ""}</h3><dl class="g-lista">{dl}</dl></section>')
    return "".join(out)

def teste_final(m):
    blocos = re.findall(r":::teste\n(.*?)\n:::", m["body"], re.S); out = []
    for k, b in enumerate(blocos):
        out.append(slide(m, k + 1, "teste", "", b.split("\n"), []).replace('class="slide s-teste"', 'class="slide s-teste final" data-final'))
    out.append(f'<section class="slide s-placar" id="cap99-fim" data-cap="99" data-cap-nome="Teste final" data-final>{cab(m, 0, 0)}<div class="placar"><span>Seu resultado</span><b>0</b><span class="pl-txt"></span></div>'
               f'<div class="pl-sera">{serafina("joinha")}</div><p class="pl-msg">Errou alguma? Volte ao capítulo indicado na explicação e leia de novo antes da próxima visita.</p></section>')
    return "".join(out)

# ------------------------------------------------------------------ capa, sumário e montagem
ORDEM = [f"cap{n:02d}.md" for n in range(15)] + ["checklist.md", "glossario.md", "teste-final.md"]
TRILHAS = [("Primeiro dia", "Para quem está começando. Leia em ordem antes da primeira visita.", [0, 1, 2, 3, 4, 7, 8, 9, 98]),
           ("Vendedor do distribuidor", "O que o trade espera da loja e como falar de produto.", [3, 4, 6, 10, 11, 12]),
           ("Dia de visita", "Consulta rápida no celular, dentro da loja.", [98, 2, 4, 5, 12]),
           ("Supervisor", "Para acompanhar a equipe e conferir a execução.", [2, 4, 5, 6, 13, 99])]

def capa_guia():
    return (f'<section class="slide capa-guia" id="inicio" data-cap="00" data-cap-nome="Guia de execução no PDV">'
            f'{animais_geo("geo cg-geo")}<div class="cg-pets">{recorte("estudio-cao-golden-01", "cg-pet a", "Golden retriever", FOTO)}{recorte("estudio-gato-branco", "cg-pet b", "Gato branco", FOTO)}</div>'
            f'<div class="cg-txt"><img class="cg-logo" src="assets/marca/logo-negativo.svg" alt="Ourofino Saúde Animal" width="320" height="54">'
            f'<span class="cg-manus">seu guia dentro da loja</span><h1>Guia de execução no ponto de venda</h1>'
            f'<p>Da preparação da visita à prateleira ideal. Para promotores, vendedores do distribuidor e equipes de loja da Ourofino Pet.</p>'
            f'<div class="cg-bts"><a class="bt" href="#cap00">Começar {icone("seta")}</a><a class="bt claro" href="#sumario">Sumário</a><button type="button" class="bt claro" data-pdf>Baixar PDF</button></div>'
            f'<span class="cg-ver">Versão 4 · novembro de 2026 · em validação com a Ourofino</span></div></section>')

def sumario(caps):
    por = {m["n"]: m for m in caps}
    def item(n):
        m = por.get(n);
        if not m: return ""
        return f'<li><a href="#cap{n:02d}"><span class="sm-n">{n if n < 97 else ""}</span><span class="sm-t">{inline(m["titulo"])}</span><span class="sm-tp">{esc(m.get("tempo", ""))}</span></a></li>'
    capsn = [m["n"] for m in caps if m["n"] < 97]; meio = (len(capsn) + 1) // 2
    s1 = (f'<section class="slide s-sumario" id="sumario" data-cap="01" data-cap-nome="Sumário"><h3 class="tit">Sumário</h3>'
          f'<ol class="sm-col">{"".join(item(n) for n in capsn[:meio])}</ol><ol class="sm-col">{"".join(item(n) for n in capsn[meio:])}</ol>'
          f'<ol class="sm-ap">{"".join(item(n) for n in (98, 97, 99))}</ol></section>')
    tri = "".join(f'<div class="tr"><h4>{t}</h4><p>{d}</p><div class="tr-c">' + "".join(f'<a href="#cap{n:02d}">{(str(n) + ". ") if n < 97 else ""}{inline(por[n]["titulo"]) if n in por else ""}</a>' for n in ns) + "</div></div>" for t, d, ns in TRILHAS)
    s2 = f'<section class="slide s-trilhas" id="trilhas" data-cap="01" data-cap-nome="Trilhas de leitura"><div class="tr-sera">{serafina("aponta")}</div><div class="tr-q"><h3 class="tit">Por onde começar</h3><div class="tr-g">{tri}</div></div></section>'
    return s1 + s2

def ler():
    caps = []
    for a in ORDEM:
        p = os.path.join(C, a)
        if not os.path.exists(p): continue
        meta, body = front(open(p, encoding="utf-8").read())
        meta["n"] = int(meta["cap"]); meta["body"] = body; caps.append(meta)
    return caps

def capitulo(m):
    n = m["n"]; out = [capa_cap(m)]
    if n == 98: return out[0] + checklist(m)
    if n == 97: return out[0] + glossario(m)
    if n == 99: return out[0] + teste_final(m)
    sl = slides_do(m["body"]); k = 0; pend = []
    lista = []
    for tipo, tit, linhas in sl:
        if tipo == "validar":
            if lista: lista[-1][3].append(" ".join(l.strip() for l in linhas if l.strip()))
            continue
        lista.append([tipo, tit, linhas, []])
    for tipo, tit, linhas, notas in lista:
        k += 1; out.append(slide(m, k, tipo, tit, linhas, notas))
    if n == 1: out.append(sumario(CAPS_GLOBAL))
    return "".join(out)

CAPS_GLOBAL = []

def montar():
    global CAPS_GLOBAL
    caps = ler(); CAPS_GLOBAL = caps
    corpo = capa_guia() + "".join(capitulo(m) for m in caps)
    nval = corpo.count('class="validar"')
    css = (open(os.path.join(AQUI, "estrutura.css"), encoding="utf-8").read() + CSS_ICONES
           + open(os.path.join(AQUI, "visual.css"), encoding="utf-8").read())
    js = open(os.path.join(AQUI, "deck.js"), encoding="utf-8").read()
    indice = "".join(f'<li><a href="#cap{m["n"]:02d}" data-cap="{m["n"]:02d}"><span>{m["n"] if m["n"] < 97 else ""}</span>{inline(m["titulo"])}</a></li>' for m in caps)
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Guia de Execução no PDV · Ourofino Pet</title>
<meta name="description" content="Guia de execução no ponto de venda da Ourofino Pet, em slides, para promotores, vendedores do distribuidor e equipes de loja.">
<meta name="theme-color" content="#072047">
<link rel="icon" href="assets/marca/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Young+Serif&family=Poppins:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Caveat:wght@600;700&display=swap" rel="stylesheet">
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
<h3>Índice</h3><ol>{indice}</ol><a class="ind-tr" href="#trilhas">Trilhas de leitura por papel</a></div></div>
<script>{js}</script>
</body>
</html>"""

if __name__ == "__main__":
    out = montar()
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(out)
    print("index.html", len(out) // 1024, "KB", out.count('class="slide'), "slides")
