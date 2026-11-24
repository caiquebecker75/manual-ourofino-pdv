"""Gera o index.html do guia a partir de conteudo/*.md (blocos ::: descritos em conteudo/_ESPEC.md).
Rodar da raiz: python3 tools/build.py  ->  index.html"""
import html, json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from diagramas import DIAGRAMAS, mascote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = os.path.join(ROOT, "conteudo")
IMG = "assets/img/"
ANOT = json.load(open(os.path.join(ROOT, "assets/render/anot.json"))) if os.path.exists(os.path.join(ROOT, "assets/render/anot.json")) else {}

# ------------------------------------------------------------------ leitura
def front(txt):
    m = re.match(r"^---\n(.*?)\n---\n", txt, re.S)
    meta, key = {}, None
    for line in m.group(1).split("\n"):
        if line.startswith("  - "): meta[key].append(line[4:].strip())
        elif ":" in line:
            k, v = line.split(":", 1); key = k.strip(); v = v.strip()
            meta[key] = v if v else []
    return meta, txt[m.end():]

def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r'"([^"\n]+)"', "“\\1”", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
    s = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\b([Cc]apítulos?) (\d{1,2})\b", lambda m: f'<a class="xref" href="#cap{int(m.group(2)):02d}">{m.group(0)}</a>', s)
    return s

def slug(s):
    import unicodedata
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")

def parse(body):
    L = body.split("\n"); i = 0; out = []
    def bloco_inicio(l): return l.startswith(":::") and l.strip() != ":::"
    while i < len(L):
        l = L[i]
        if bloco_inicio(l):
            nome, _, arg = l[3:].partition(" "); j = i + 1; buf = []
            while j < len(L) and L[j].strip() != ":::": buf.append(L[j]); j += 1
            out.append(("bloco", nome.strip(), arg.strip(), buf)); i = j + 1; continue
        if l.startswith("## "): out.append(("h2", l[3:].strip())); i += 1; continue
        if l.startswith("### "): out.append(("h3", l[4:].strip())); i += 1; continue
        if l.startswith("|"):
            buf = []
            while i < len(L) and L[i].startswith("|"): buf.append(L[i]); i += 1
            out.append(("tabela", buf)); continue
        if re.match(r"^- \[[ x]\] ", l):
            buf = []
            while i < len(L) and re.match(r"^- \[[ x]\] ", L[i]): buf.append(L[i][6:]); i += 1
            out.append(("check", buf)); continue
        if l.startswith("- "):
            buf = []
            while i < len(L) and L[i].startswith("- "): buf.append(L[i][2:]); i += 1
            out.append(("ul", buf)); continue
        if re.match(r"^\d+\. ", l):
            buf = []
            while i < len(L) and re.match(r"^\d+\. ", L[i]): buf.append(re.sub(r"^\d+\. ", "", L[i])); i += 1
            out.append(("ol", buf)); continue
        if not l.strip(): i += 1; continue
        buf = []
        while i < len(L) and L[i].strip() and not bloco_inicio(L[i]) and not L[i].startswith(("#", "|", "- ")) and not re.match(r"^\d+\. ", L[i]):
            buf.append(L[i].strip()); i += 1
        out.append(("p", " ".join(buf)))
    return out

# ------------------------------------------------------------------ ícones de traço
def svg(path, s=20, cls="i"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" width="{s}" height="{s}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{path}</svg>'
I_OK = svg('<path d="M5 12.5l4.5 4.5L19 7.5"/>')
I_X = svg('<path d="M6.5 6.5l11 11M17.5 6.5l-11 11"/>')
I_MAIS = svg('<path d="M12 5v14M5 12h14"/>')
I_SETA = svg('<path d="M5 12h14M13 6l6 6-6 6"/>')
I_ALERTA = svg('<path d="M12 3.5l9.5 16.5h-19z"/><path d="M12 10v4.5M12 17.6v.1"/>')
I_LIVRO = svg('<path d="M4 5.5C4 4.7 4.7 4 5.5 4H11v15H5.5A1.5 1.5 0 0 1 4 17.5z"/><path d="M20 5.5c0-.8-.7-1.5-1.5-1.5H13v15h5.5a1.5 1.5 0 0 0 1.5-1.5z"/>')
I_RELOGIO = svg('<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>', 16)
I_PESSOA = svg('<circle cx="12" cy="8" r="3.5"/><path d="M5 20c.8-3.8 3.6-6 7-6s6.2 2.2 7 6"/>', 16)
I_MENU = svg('<path d="M4 7h16M4 12h16M4 17h10"/>', 22)
I_PDF = svg('<path d="M12 4v11M7 10.5l5 5 5-5"/><path d="M5 19.5h14"/>', 18)
I_LUPA = svg('<circle cx="11" cy="11" r="6.5"/><path d="M16 16l4 4"/>', 18)
I_REV = svg('<path d="M4 20h4L19 9l-4-4L4 16z"/><path d="M13.5 6.5l4 4"/>', 18)

# ------------------------------------------------------------------ figuras
FIGN = {}
def dims(fid):
    f = os.path.join(ROOT, IMG + fid.lower() + ".webp")
    if not os.path.exists(f): return (1800, 1200)
    from PIL import Image
    return Image.open(f).size

def img_tag(fid, alt, sizes="(min-width: 1100px) 1040px, 100vw", cls="", lazy=True):
    base = IMG + fid.lower(); w, h = dims(fid)
    if fid.startswith("P-"):
        return f'<img class="{cls}" src="{base}.webp" width="{w}" height="{h}" alt="{html.escape(alt)}" loading="lazy" decoding="async">'
    ld = ' loading="lazy"' if lazy else ' fetchpriority="high"'
    return (f'<img class="{cls}" src="{base}.webp" srcset="{base}-900.webp 900w, {base}.webp 1800w" sizes="{sizes}" '
            f'width="{w}" height="{h}" alt="{html.escape(alt)}"{ld} decoding="async">')

ROTULOS = {  # (âncora, título, detalhe, cor do ponto, posição do texto)
    "F-GONDOLA-ZONAS": [("olhos_meio", "Zona dos olhos", "1,20 m a 1,60 m · zona quente", "q", "esq"),
                        ("maos_meio", "Zona das mãos", "0,80 m a 1,20 m", "m", "esq"),
                        ("pes_meio", "Zona dos pés", "abaixo de 0,80 m", "p", "esq")],
    "F-PRATELEIRA-IDEAL": [("antipulga", "Antipulgas", "WellPET e Leevre juntos", "", "acima"),
                           ("concorrente", "Concorrente ao lado", "na mesma altura", "", "abaixo"),
                           ("vermifugo", "Vermífugos", "Top Dog por faixa de peso", "", "acima"),
                           ("suplementos", "Suplementos", "pele e pelo juntos", "", "abaixo")],
    "F-PONTO-EXTRA-ERRADO": [("buraco", "Buraco na gôndola", "o produto saiu do ponto natural", "x", "auto"), ("display", "Display cheio", "", "", "auto")],
    "F-PONTO-EXTRA-CERTO": [("buraco", "Gôndola cheia", "o ponto natural continua abastecido", "ok", "auto"), ("display", "Estoque extra no display", "", "", "auto")],
}
def rotulos(fid):
    pts = ANOT.get(fid, {}); out = []
    for k, t, s, tipo, pos in ROTULOS.get(fid, []):
        if k not in pts: continue
        x, y = pts[k]
        if pos == "auto": pos = "esq" if x > 62 else "dir"
        txt = f"<span class=pino-txt><b>{t}</b>{f'<small>{s}</small>' if s else ''}</span>"
        out.append(f'<span class="pino {tipo} {pos}" style="left:{x:.1f}%;top:{y:.1f}%"><i></i>{txt}</span>')
    return "".join(out)

def figura(cap, fid, legenda, extra_cls=""):
    FIGN[cap] = FIGN.get(cap, 0) + 1; n = f"{cap}.{FIGN[cap]}"
    leg = inline(" ".join(x.strip() for x in legenda if x.strip()))
    cap_html = f'<figcaption><span class="fig-n">Figura {n}</span>{leg}</figcaption>'
    if fid.startswith("D-"):
        return f'<figure class="fig dg-fig {extra_cls}" id="fig-{fid.lower()}">{DIAGRAMAS[fid]()}{cap_html}</figure>'
    if fid.startswith("P-"):
        return f'<figure class="fig prod {extra_cls}">{img_tag(fid, leg)}{cap_html}</figure>'
    rot = rotulos(fid)
    btn = '<button class="rot-btn" type="button" aria-pressed="true">Ocultar marcações</button>' if rot else ""
    return (f'<figure class="fig foto {extra_cls}" id="fig-{fid.lower()}"><div class="foto-quadro">{img_tag(fid, re.sub("<.*?>", "", leg))}'
            f'{f"<div class=rot>{rot}</div>" if rot else ""}{btn}</div>{cap_html}</figure>')

def comparador(cap, a, b, la, lb, ta, tb):
    FIGN[cap] = FIGN.get(cap, 0) + 1; n = f"{cap}.{FIGN[cap]}"
    leg_a = inline(" ".join(x.strip() for x in la)); leg_b = inline(" ".join(x.strip() for x in lb))
    w, h = dims(b)
    return (f'<figure class="fig comp" data-comp><div class="comp-quadro" style="max-width:min(100%,calc(80vh * {w / h:.4f}))">'
            f'<div class="comp-b">{img_tag(b, re.sub("<.*?>", "", leg_b))}{f"<div class=rot>{rotulos(b)}</div>"}</div>'
            f'<div class="comp-a">{img_tag(a, re.sub("<.*?>", "", leg_a))}{f"<div class=rot>{rotulos(a)}</div>"}</div>'
            f'<span class="comp-tag a">{ta}</span><span class="comp-tag b">{tb}</span>'
            f'<div class="comp-linha"><span>{I_SETA}{I_SETA}</span></div>'
            f'<input class="comp-range" type="range" min="0" max="100" value="50" aria-label="Arraste para comparar {ta.lower()} e {tb.lower()}"></div>'
            f'<figcaption><span class="fig-n">Figura {n}</span><span class="comp-leg"><b>{ta}.</b> {leg_a}</span>'
            f'<span class="comp-leg"><b>{tb}.</b> {leg_b}</span></figcaption></figure>')

# ------------------------------------------------------------------ blocos
TESTE_N = [0]
def bloco(cap, nome, arg, buf, ctx):
    txt = [x for x in buf]
    if nome == "dica":
        return (f'<aside class="dica"><div class="dica-av">{mascote(52)}</div><div class="dica-balao">'
                f'<span class="rotulo">Dica da turma</span><p>{inline(" ".join(t.strip() for t in txt if t.strip()))}</p></div></aside>')
    if nome == "erro":
        j = " ".join(t.strip() for t in txt)
        m = re.match(r"\*\*O que acontece:\*\*(.*?)\*\*Faça assim:\*\*(.*)", j, re.S)
        a, b = (m.group(1).strip(), m.group(2).strip()) if m else (j, "")
        return (f'<aside class="erro"><div class="erro-lado ruim"><span class="rotulo">{I_ALERTA} Erro comum</span><p>{inline(a)}</p></div>'
                f'<div class="erro-lado bom"><span class="rotulo">{I_OK} Faça assim</span><p>{inline(b)}</p></div></aside>')
    if nome == "passos":
        lis = []
        for t in txt:
            t = re.sub(r"^\d+\.\s*", "", t.strip())
            if not t: continue
            m = re.match(r"\*\*(.+?)\*\*\s*·\s*(.*)", t)
            lis.append(f"<li><b>{inline(m.group(1))}</b><span>{inline(m.group(2))}</span></li>" if m else f"<li><span>{inline(t)}</span></li>")
        return f'<ol class="passos">{"".join(lis)}</ol>'
    if nome == "certo-errado":
        bons = [inline(t[1:].strip()) for t in txt if t.startswith("+")]
        maus = [inline(t[1:].strip()) for t in txt if t.startswith("-")]
        return (f'<div class="ce"><div class="ce-col certo"><span class="rotulo">{I_OK} Faça</span><ul>{"".join(f"<li>{x}</li>" for x in bons)}</ul></div>'
                f'<div class="ce-col errado"><span class="rotulo">{I_X} Evite</span><ul>{"".join(f"<li>{x}</li>" for x in maus)}</ul></div></div>')
    if nome == "termo":
        ctx["termos"].append(arg)
        return (f'<div class="termo" id="termo-{slug(arg)}"><span class="rotulo">Termo</span><dfn>{html.escape(arg)}</dfn>'
                f'<p>{inline(" ".join(t.strip() for t in txt if t.strip()))}</p></div>')
    if nome == "frase":
        falas = []
        for t in txt:
            if not t.strip(): continue
            quem, _, fala = t.partition(":")
            q = quem.strip().lower(); lado = "eu" if q in ("você", "voce", "promotor", "promotora") else "outro"
            falas.append(f'<div class="fala {lado}"><span class="quem">{html.escape(quem.strip())}</span><p>{inline(fala.strip())}</p></div>')
        return f'<div class="conversa"><span class="rotulo">Na prática</span>{"".join(falas)}</div>'
    if nome == "saibamais":
        inner = render_nos(cap, parse("\n".join(txt)), ctx, interno=True)
        return (f'<details class="saiba"><summary><span class="rotulo">Saiba mais</span><b>{inline(arg)}</b>'
                f'<span class="saiba-ic">{I_MAIS}</span></summary><div class="saiba-corpo">{inner}</div></details>')
    if nome == "fig":
        return figura(cap, arg, txt)
    if nome == "teste":
        TESTE_N[0] += 1
        q = ""; ops = []; exp = []
        for t in txt:
            s = t.strip()
            if s.startswith("?"): q = s[1:].strip()
            elif s.startswith("- [x]"): ops.append((True, s[5:].strip()))
            elif s.startswith("- [ ]"): ops.append((False, s[5:].strip()))
            elif s.startswith(">"): exp.append(s[1:].strip())
        bts = "".join(f'<button type="button" class="op" data-ok="{1 if ok else 0}"><span class="op-l">{chr(65 + k)}</span><span>{inline(o)}</span></button>'
                      for k, (ok, o) in enumerate(ops))
        return (f'<div class="teste" data-teste><span class="rotulo">Teste rápido</span><p class="teste-q">{inline(q)}</p>'
                f'<div class="ops">{bts}</div><div class="teste-exp" hidden><b class="teste-res"></b> {inline(" ".join(exp))}</div></div>')
    if nome == "validar":
        return f'<aside class="validar"><span class="rotulo">Para a Ourofino validar</span><p>{inline(" ".join(t.strip() for t in txt if t.strip()))}</p></aside>'
    if nome == "cards":
        cs = []
        for t in txt:
            m = re.match(r"\*\*(.+?)\*\*\s*·\s*(.*)", t.strip())
            if m: cs.append(f'<div class="card"><b>{inline(m.group(1))}</b><p>{inline(m.group(2))}</p></div>')
        return f'<div class="cards n{len(cs)}">{"".join(cs)}</div>'
    if nome == "cbv":
        d = {}
        for t in txt:
            m = re.match(r"^([CBV]):\s*(.*)", t.strip())
            if m: d[m.group(1)] = m.group(2)
        nomes = {"C": "Característica", "B": "Benefício", "V": "Vantagem"}
        return ('<div class="cbv">' + "".join(f'<div class="cbv-p"><span class="cbv-l">{k}</span><span class="rotulo">{nomes[k]}</span><p>{inline(d.get(k, ""))}</p></div>'
                                              for k in "CBV") + "</div>")
    return f"<!-- bloco desconhecido {nome} -->"

def tabela(buf):
    rows = [[c.strip() for c in r.strip().strip("|").split("|")] for r in buf if not re.match(r"^\|[\s:|-]+\|$", r.strip())]
    cab, corpo = rows[0], rows[1:]
    th = "".join(f"<th>{inline(c)}</th>" for c in cab)
    trs = "".join("<tr>" + "".join(f'<td data-l="{html.escape(re.sub(r"[*]", "", cab[k]))}">{inline(c)}</td>' for k, c in enumerate(r)) + "</tr>" for r in corpo)
    return f'<div class="tabela"><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>'

def render_nos(cap, nos, ctx, interno=False):
    out = []; k = 0
    while k < len(nos):
        n = nos[k]; t = n[0]
        if t == "bloco":
            nome, arg, buf = n[1], n[2], n[3]
            nxt = nos[k + 1] if k + 1 < len(nos) else None
            par = {("F-ANTES", "F-DEPOIS"): ("Antes", "Depois"), ("F-PONTO-EXTRA-ERRADO", "F-PONTO-EXTRA-CERTO"): ("Errado", "Certo")}
            if nome == "fig" and nxt and nxt[0] == "bloco" and nxt[1] == "fig" and (arg, nxt[2]) in par:
                ta, tb = par[(arg, nxt[2])]
                out.append(comparador(cap, arg, nxt[2], buf, nxt[3], ta, tb)); k += 2; continue
            if nome == "fig" and arg.startswith("P-") and nxt and nxt[0] == "bloco" and nxt[1] == "cards":
                out.append(f'<div class="ficha">{figura(cap, arg, buf)}{bloco(cap, "cards", "", nxt[3], ctx)}</div>'); k += 2; continue
            if nome == "termo":
                grupo = []
                while k < len(nos) and nos[k][0] == "bloco" and nos[k][1] == "termo":
                    grupo.append(bloco(cap, "termo", nos[k][2], nos[k][3], ctx)); k += 1
                out.append(f'<div class="termos{" um" if len(grupo) == 1 else ""}">{"".join(grupo)}</div>'); continue
            out.append(bloco(cap, nome, arg, buf, ctx))
        elif t == "h2":
            ctx["sec"] += 1; sid = f"cap{cap:02d}-{ctx['sec']}"
            ctx["secoes"].append((sid, n[1]))
            num = f'<span class="sec-n">{cap}.{ctx["sec"]}</span>' if cap < 97 else ""
            out.append(f'<h2 class="sec" id="{sid}">{num}{inline(n[1])}</h2>')
        elif t == "h3": out.append(f"<h3>{inline(n[1])}</h3>")
        elif t == "p": out.append(f"<p>{inline(n[1])}</p>")
        elif t == "ul": out.append("<ul class=\"lista\">" + "".join(f"<li>{inline(x)}</li>" for x in n[1]) + "</ul>")
        elif t == "ol": out.append("<ol class=\"lista\">" + "".join(f"<li>{inline(x)}</li>" for x in n[1]) + "</ol>")
        elif t == "tabela": out.append(tabela(n[1]))
        elif t == "check":
            for x in n[1]:
                ctx["chk"] += 1
                out.append(f'<label class="chk"><input type="checkbox" data-k="c{ctx["chk"]}"><span class="chk-box">{I_OK}</span><span>{inline(x)}</span></label>')
        k += 1
    return "".join(out)

# ------------------------------------------------------------------ capítulos
ARQS = [f"cap{n:02d}.md" for n in range(13)] + ["glossario.md", "checklist.md", "teste-final.md"]
ABRE = {0: "F-LOJA", 1: "O-CORREDOR", 2: "O-ENTRADA", 3: "O-BALCAO", 4: "F-MAT-DISPLAY-BALCAO", 5: "O-MACRO", 6: "F-MAT-ILHA",
        7: "O-FARMACIA", 8: "O-ALTO", 9: "O-RACAO", 10: "F-MAT-TAKEONE", 12: "F-MAT-ADESIVO-CHAO"}
POS = {0: "50% 60%", 1: "50% 55%", 2: "50% 55%", 3: "50% 45%", 4: "50% 60%", 5: "35% 50%", 6: "50% 55%", 7: "50% 45%",
       8: "50% 55%", 9: "50% 50%", 10: "50% 55%", 12: "50% 45%"}
PARTES = [("Abertura", [0]), ("1 · Entender", [1, 2]), ("2 · A visita", [3, 4]), ("3 · Na gôndola", [5, 6, 7]),
          ("4 · Materiais e cross", [8, 9]), ("5 · Produtos", [10, 11]), ("6 · Postura", [12]), ("Fechamento", [97, 98, 99])]
TRILHAS = [
    ("Primeiro dia", "Para quem está começando como promotor. Leia nesta ordem, do começo ao fim, antes da primeira visita.", [0, 1, 2, 3, 4, 5, 6, 12, 98]),
    ("Vendedor do distribuidor", "Você já conhece o cliente. Aqui está o que o trade espera da loja e como falar de produto.", [1, 2, 5, 6, 9, 10, 11]),
    ("Dia de visita", "Consulta rápida no celular, dentro da loja. Abra direto no que precisa.", [98, 3, 5, 8, 11]),
    ("Supervisor", "Para acompanhar a equipe e conferir a execução nas fotos de antes e depois.", [3, 5, 7, 8, 9, 99]),
]

def ler():
    caps = []
    for a in ARQS:
        meta, body = front(open(os.path.join(C, a), encoding="utf-8").read())
        meta["n"] = int(meta["cap"]); meta["body"] = body; caps.append(meta)
    return caps

def abertura(m, ctx):
    n = m["n"]; nn = f"{n:02d}"
    vv = "".join(f"<li>{I_OK}<span>{inline(x)}</span></li>" for x in m.get("voce_vai", []))
    secs = "".join(f'<li><a href="#{sid}"><span>{n}.{k + 1}</span>{inline(t)}</a></li>' for k, (sid, t) in enumerate(ctx["secoes"]))
    meta = (f'<div class="ab-meta"><span>{I_PESSOA}{html.escape(m.get("publico", ""))}</span>'
            f'<span>{I_RELOGIO}{html.escape(m.get("tempo", ""))}</span></div>')
    if n in ABRE:
        vis = (f'<div class="ab-img">{img_tag(ABRE[n], "", sizes="100vw")}</div>')
        vis = vis.replace("<img ", f'<img style="object-position:{POS.get(n, "50% 50%")}" ', 1)
        cls = "com-img"
    elif n == 11:
        prods = ["P-WELLPET", "P-BANNI3", "P-TOPDOG", "P-LEEVRE", "P-HERBALVET", "P-ENZICLIM", "P-PLENIPIL"]
        vis = '<div class="ab-img ab-prods">' + "".join("<span>" + img_tag(p, p[2:].title()).replace(' loading="lazy"', "") + "</span>" for p in prods) + "</div>"
        cls = "com-img prods"
    else:
        vis = ""; cls = "tipo"
    num = "" if n >= 97 else f'<span class="ab-num" aria-hidden="true">{nn}</span>'
    kicker = m["parte"] if n >= 97 else f'Capítulo {nn} · {m["parte"]}'
    ind = f'<nav class="ab-secoes" aria-label="Seções do capítulo"><span class="rotulo">Neste capítulo</span><ol>{secs}</ol></nav>' if secs and n < 97 else ""
    voce = f'<div class="ab-voce"><span class="rotulo">Você vai</span><ul>{vv}</ul></div>' if vv else ""
    return (f'<header class="abertura {cls}">{vis}<div class="ab-txt">{num}<span class="ab-kicker">{html.escape(kicker)}</span>'
            f'<h1 class="ab-titulo">{inline(m["titulo"])}</h1><p class="ab-frase">{inline(m.get("capa_frase", ""))}</p>{meta}'
            f'<div class="ab-grade">{voce}{ind}</div></div></header>')

def glossario(m):
    nos = parse(m["body"]); letras = []; itens = []
    for n in nos:
        if n[0] == "h2": letras.append(n[1]); itens.append(f'<h2 class="g-letra" id="g-{n[1].lower()}">{n[1]}</h2>')
        elif n[0] == "p":
            mm = re.match(r"\*\*(.+?)\*\*\s*·\s*(.*)", n[1])
            if not mm: itens.append(f"<p>{inline(n[1])}</p>"); continue
            termo, resto = mm.group(1), mm.group(2)
            ex = ""
            if "Exemplo:" in resto: resto, ex = resto.split("Exemplo:", 1)
            itens.append(f'<div class="g-item" data-busca="{html.escape(slug(termo + " " + resto))}"><dt>{html.escape(termo)}</dt>'
                         f'<dd>{inline(resto.strip())}{f"<span class=g-ex><b>Exemplo</b> {inline(ex.strip())}</span>" if ex else ""}</dd></div>')
    nav = "".join(f'<a href="#g-{l.lower()}">{l}</a>' for l in letras)
    return (f'<div class="g-ferr"><label class="g-busca">{I_LUPA}<input type="search" placeholder="Buscar um termo" aria-label="Buscar no glossário"></label>'
            f'<nav class="g-az" aria-label="Letras">{nav}</nav></div><div class="g-lista">{"".join(itens)}</div><p class="g-vazio" hidden>Nenhum termo encontrado.</p>')

def capitulo(m):
    n = m["n"]; ctx = {"sec": 0, "secoes": [], "termos": [], "chk": 0 if n != 98 else 0}
    if n == 97:
        corpo = glossario(m); ctx["secoes"] = []
    else:
        corpo = render_nos(n, parse(m["body"]), ctx)
    extra = ""
    if n == 98:
        extra = ('<div class="chk-barra"><span class="chk-prog"><i></i></span><span class="chk-txt">0 de 0 itens</span>'
                 '<button type="button" class="bt-sec" data-limpar>Limpar marcações</button></div>')
    if n == 99:
        extra = '<div class="placar" aria-live="polite"><span class="rotulo">Seu resultado</span><b>0</b><span class="pl-txt"></span></div>'
    cls = {97: "glossario", 98: "checklist", 99: "final"}.get(n, "")
    return (f'<section class="cap {cls}" id="cap{n:02d}" data-titulo="{html.escape(m["titulo"])}">{abertura(m, ctx)}'
            f'<div class="cap-corpo">{extra}{corpo}</div></section>')

def sumario(caps):
    por = {m["n"]: m for m in caps}
    blocos = []
    for nome, ns in PARTES:
        li = "".join(f'<li><a href="#cap{n:02d}"><span class="s-n">{"" if n >= 97 else f"{n:02d}"}</span><span class="s-t">{inline(por[n]["titulo"])}</span>'
                     f'<span class="s-tempo">{html.escape(por[n].get("tempo", ""))}</span></a></li>' for n in ns)
        blocos.append(f'<div class="s-parte"><h3>{nome}</h3><ol>{li}</ol></div>')
    tri = []
    for k, (t, d, ns) in enumerate(TRILHAS):
        chips = "".join(f'<a href="#cap{n:02d}"><span>{"" if n >= 97 else f"{n:02d}"}</span>{inline(por[n]["titulo"])}</a>' for n in ns)
        tri.append(f'<div class="trilha"><span class="rotulo">Trilha {k + 1}</span><h3>{t}</h3><p>{d}</p><div class="tri-chips">{chips}</div></div>')
    return (f'<section class="sumario" id="sumario"><div class="sum-cab"><span class="rotulo">Sumário</span>'
            f'<h2>O guia em seis partes</h2><p>Leia em ordem na primeira vez. Depois, use como consulta: cada capítulo funciona sozinho.</p></div>'
            f'<div class="sum-grade"><div class="sum-caps">{"".join(blocos)}</div>'
            f'<div class="sum-trilhas"><div class="tri-cab"><span class="rotulo">Trilhas de leitura</span><h3>Escolha pelo seu papel</h3></div>{"".join(tri)}</div></div></section>')

def gaveta(caps):
    num = lambda n: "" if n >= 97 else f"{n:02d}"
    li = "".join(f'<li><a href="#cap{m["n"]:02d}"><span>{num(m["n"])}</span>{inline(m["titulo"])}</a></li>' for m in caps)
    return (f'<div class="gaveta" id="gaveta" hidden><div class="gav-fundo" data-fecha></div><nav class="gav-painel" aria-label="Capítulos">'
            f'<div class="gav-topo"><span class="rotulo">Capítulos</span><button type="button" class="bt-ic" data-fecha aria-label="Fechar">{I_X}</button></div>'
            f'<ol>{li}</ol><a class="gav-sum" href="#sumario">Ver sumário completo e trilhas</a></nav></div>')

def capa():
    return (f'<section class="capa" id="inicio"><div class="capa-img">{img_tag("F-CAPA", "Petshop com a farmácia organizada atrás do balcão", sizes="100vw", lazy=False)}</div>'
            f'<img class="capa-logo-fixo" src="assets/marca/ourofino_negativo_branco.png" alt="Ourofino Saúde Animal"><div class="capa-txt">'
            f'<span class="capa-kicker">Ourofino Pet · Trade marketing</span>'
            f'<h1>Guia de execução no ponto de venda</h1>'
            f'<p>O que fazer antes, durante e depois da visita, da gôndola ao balcão. Para promotores, vendedores do distribuidor e equipes de loja.</p>'
            f'<div class="capa-bts"><a class="bt" href="#cap00">Começar a leitura {I_SETA}</a><a class="bt claro" href="#sumario">Sumário</a>'
            f'<button type="button" class="bt claro" data-pdf>{I_PDF} Baixar PDF</button></div>'
            f'<span class="capa-ver">Versão 2 · novembro de 2026 · em validação com a Ourofino</span></div></section>')

def montar():
    caps = ler()
    corpo = "".join(capitulo(m) for m in caps)
    nval = corpo.count('class="validar"')
    aviso = (f'<p class="sum-rev">{I_REV}<span><b>Equipe Ourofino:</b> toque em <b>Revisão</b>, no topo da página, para ver as {nval} notas em amarelo '
             f'com o que precisa da sua validação antes da versão final.</span></p>')
    sumario_html = sumario(caps).replace('</p></div><div class="sum-grade">', '</p>' + aviso + '</div><div class="sum-grade">', 1)
    css = open(os.path.join(ROOT, "tools/guia.css"), encoding="utf-8").read()
    js = open(os.path.join(ROOT, "tools/guia.js"), encoding="utf-8").read()
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Guia de Execução no PDV · Ourofino Pet</title>
<meta name="description" content="Guia de execução no ponto de venda da Ourofino Pet para promotores, vendedores do distribuidor e equipes de loja.">
<meta name="theme-color" content="#072047">
<link rel="icon" href="assets/marca/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght,SOFT@9..144,400..800,100&family=Figtree:ital,wght@0,400..800;1,400..600&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="preload" as="image" href="{IMG}f-capa.webp" imagesrcset="{IMG}f-capa-900.webp 900w, {IMG}f-capa.webp 1800w" imagesizes="100vw">
<style>{css}</style>
</head>
<body>
<a class="pular" href="#cap00">Pular para o conteúdo</a>
<header class="topo"><a class="topo-logo" href="#inicio" aria-label="Início"><img src="assets/marca/ourofino_positivo_semslogan.png" alt="Ourofino"></a>
<span class="topo-cap" aria-live="polite"></span>
<div class="topo-bts"><button type="button" class="bt-ic rev" data-rev aria-pressed="false" title="Modo revisão: mostra as notas para a Ourofino validar">{I_REV}<span>Revisão</span></button>
<button type="button" class="bt-ic" data-pdf title="Baixar PDF">{I_PDF}<span>PDF</span></button>
<button type="button" class="bt-ic" data-abre title="Capítulos">{I_MENU}<span>Capítulos</span></button></div>
<span class="topo-prog"><i></i></span></header>
{gaveta(caps)}
<main>
{capa()}
{sumario_html}
{corpo}
</main>
<footer class="rodape"><img src="assets/marca/ourofino_negativo_branco.png" alt="Ourofino Saúde Animal">
<p>Guia de execução no ponto de venda · Ourofino Pet · versão 2, novembro de 2026.<br>Material de uso interno da equipe de trade e dos parceiros. As informações de produto seguem o site oficial ourofinopet.com; em caso de dúvida técnica, consulte o veterinário ou o material oficial.</p>
<a class="bt claro" href="#inicio">Voltar ao início</a></footer>
<script>{js}</script>
</body>
</html>"""

if __name__ == "__main__":
    out = montar()
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(out)
    print("index.html", len(out) // 1024, "KB")
