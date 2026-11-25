#!/usr/bin/env python3
"""Cronograma de aprovação e pacotes por etapa do Guia de Execução no PDV (Ourofino Pet).

Roda depois do livro.py, sempre a partir do index.html já construído:
    python3 tools/v6/livro.py
    python3 tools/v6/etapas.py                    # pacotes + miniaturas + cronograma
    python3 tools/v6/etapas.py --sem-miniaturas   # só o HTML (mantém as miniaturas que já existem)
    python3 tools/v6/etapas.py --perfil /tmp/x    # pasta de perfil do Chrome headless (padrão: temporária)

Gera:
    aprovacao/etapa-N/index.html    o guia recortado, com as páginas na numeração do guia completo
    aprovacao/miniaturas/pNN.webp   uma miniatura por página do guia completo (Chrome headless + PyMuPDF)
    cronograma/index.html           documento para a Ourofino aprovar etapa por etapa

As fronteiras das etapas saem do data-cap de cada slide (capítulos), não de posições fixas:
se o guia ganhar ou perder páginas, as páginas de cada etapa são recalculadas.
"""
import argparse, datetime as dt, html, json, os, re, shutil, socket, subprocess, sys, tempfile, time

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HOJE = dt.date.today()

# ---------------------------------------------------------------- dados do cronograma
# caps: data-cap dos slides ("FIM" = o último capítulo do guia, o fechamento)
ETAPAS = [
    dict(n=1, nome="Abertura e a visita", caps=["00", "01"], cor="#10AD31", tinta="#072047",
         envio="2026-11-26", retorno="2026-12-02", check="2026-12-03",
         conferir=["Se a Serafina representa bem o time de campo: nome, jeito e uniforme.",
                   "Se a ordem da visita (antes, os oito passos na loja e o depois) é a que vocês cobram em campo.",
                   "Se a conversa da chegada soa como o promotor de vocês fala com o balconista.",
                   "Se o kit da visita e o registro batem com o que o time tem hoje."],
         precisa=[]),
    dict(n=2, nome="Fundamentos e gôndola", caps=["02", "03", "04"], cor="#007CC1", tinta="#fff",
         envio="2026-12-03", retorno="2026-12-09", check="2026-12-10",
         conferir=["Se trade, sell-in e sell-out estão explicados para quem nunca ouviu falar.",
                   "Se o básico da gôndola (os 4 itens, FIFO, frente, blocagem e alturas) é o que vocês pedem na loja.",
                   "Se os materiais de PDV são os que a Ourofino usa e se o lugar de cada um está certo.",
                   "Se a clínica está bem retratada: onde entra material e onde não entra."],
         precisa=[("2026-12-09", "Material de ciclo de vendas e canais (a apresentação de junho)"),
                  ("2026-12-09", "Lista dos materiais de PDV que a Ourofino usa e pode usar")]),
    dict(n=3, nome="Na loja toda e as pessoas", caps=["05", "06", "07"], cor="#20D5F2", tinta="#072047",
         envio="2026-12-10", retorno="2026-12-16", check="2026-12-17",
         conferir=["Se a diferença entre cross merchandising e cross selling ficou clara.",
                   "Se os pares de cross que aparecem podem ser usados.",
                   "Se a regra do ponto extra (gôndola cheia primeiro) é a mesma de vocês.",
                   "Se o tom de relacionamento e a tabela de quem decide batem com cada tipo de loja."],
         precisa=[("2026-12-16", "Pares de cross que podem e que não podem"),
                  ("2026-12-16", "Matriz de quem decide em cada tipo de loja")]),
    dict(n=4, nome="O produto", caps=["08", "09"], cor="#072047", tinta="#fff",
         envio="2026-12-17", retorno="2027-01-13", check="2027-01-14",
         nota_retorno="prazo maior: inclui o regulatório e o fim de ano",
         conferir=["Se o CBV de cada produto usa as palavras que a Ourofino aprova.",
                   "Se os heróis e os 10 de cada categoria são esses, e nesta ordem.",
                   "Se os medicamentos podem aparecer no material do promotor, e com que texto.",
                   "Se o que pode e o que não pode dizer cobre as dúvidas do balcão."],
         precisa=[("2027-01-13", "Lista oficial de produtos heróis"),
                  ("2027-01-13", "Ranking dos 10 de cada categoria no canal petshop"),
                  ("2027-01-13", "Aprovação do regulatório para os medicamentos")]),
    dict(n=5, nome="Prateleira ideal e fechamento", caps=["10", "FIM"], cor="#0A7F23", tinta="#fff",
         envio="2027-01-14", retorno="2027-01-20", check="2027-01-21",
         conferir=["Se a prateleira ideal segue a referência de vocês.",
                   "Se as cinco regras da prateleira valem para petshop e para clínica.",
                   "Se o checklist da visita tem tudo o que o time precisa marcar.",
                   "Se as perguntas do teste final cobram o que importa."],
         precisa=[("2027-01-20", "Referência de prateleira ideal ou planograma da Ourofino")]),
]
FINAIS = [
    dict(k="A", nome="Guia completo", cor="#FFE07A", tinta="#072047",
         desc="O guia inteiro, com os ajustes das cinco etapas e a arte da turma do bite aplicada nas dicas.",
         envio="2027-01-28", retorno="2027-02-03", check="2027-02-04",
         conferir=["Se todos os ajustes pedidos nas etapas entraram.",
                   "Se a turma do bite aparece nas dicas do jeito que a marca usa.",
                   "Navegação no celular, índice, sumário e PDF."],
         precisa=[("2027-01-13", "Arte da turma do bite e os formatos disponíveis")]),
    dict(k="B", nome="Arte final", cor="#072047", tinta="#fff",
         desc="PDF para impressão e versão digital final, no link definitivo.",
         envio="2027-02-05", retorno="2027-02-12", check=None,
         conferir=["O PDF de impressão, página por página.",
                   "O link final do guia digital, no celular e no computador."],
         precisa=[]),
]
ENTREGA = "2027-02-19"
CONVENCAO = ("2027-03-01", "2027-03-05")
PAUSAS = [("2026-12-21", "2027-01-01", "Natal e Ano-Novo", "sem envios"),
          ("2027-02-08", "2027-02-09", "Carnaval", "08 e 09/02")]
G_INI, G_FIM = dt.date(2026, 11, 23), dt.date(2027, 3, 7)   # janela da linha do tempo (segunda a domingo)

NOME_CAP = {"00": "Abertura: capa, Serafina, como usar e sumário",
            "FIM": "Fechamento: considerações, checklist, teste e contracapa"}
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def D(s): return dt.date.fromisoformat(s)
def dm(s): d = D(s) if isinstance(s, str) else s; return f"{d.day:02d}/{d.month:02d}"
def dsem(s): d = D(s) if isinstance(s, str) else s; return f"{DIAS[d.weekday()]} {dm(d)}"
def esc(s): return html.escape(s, quote=True)
def limpa(h): return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h))).strip()


# ---------------------------------------------------------------- leitura do guia construído
def le_guia():
    s = open(os.path.join(R, "index.html"), encoding="utf-8").read()
    abre = '<main class="palco">'
    a, b = s.index(abre) + len(abre), s.index("</main>")
    head, corpo, cauda = s[:a], s[a:b], s[b:]
    pedacos = corpo.split('<section class="slide ')
    slides = []
    for k, p in enumerate(pedacos[1:], 1):
        h = '<section class="slide ' + p
        tag = h[:h.index(">") + 1]
        at = lambda n: (re.search(n + r'="([^"]*)"', tag) or [None, ""])[1]
        cls, sid, cap = at("class"), at("id"), at("data-cap")
        notas = [limpa(x) for x in re.findall(r'<aside class="validar"><b>[^<]*</b>(.*?)</aside>', h, re.S)]
        cap_nome = html.unescape(at("data-cap-nome"))
        tit = TIT_MD.get(sid) or titulo(cls, h)
        if tit in ("", "Abertura: "): tit = re.sub(r"^\d+\.\s*", "", cap_nome) or "Página %d" % k
        slides.append(dict(pg=k, html=h, cls=cls, id=sid, cap=cap, cap_nome=cap_nome, titulo=tit, notas=notas))
    ver = re.search(r'<span class="cg-ver">([^<]*)</span>', s)
    return dict(head=head, cauda=cauda, slides=slides, prefixo=pedacos[0], versao=html.unescape(ver.group(1)) if ver else "")


def titulos_md():
    """Título de cada página pelo conteudo-v6 (id capNN-k = k-ésimo bloco; sem capa, o 1º bloco é capNN; contracapa = fim)."""
    out, pasta = {}, os.path.join(R, "conteudo-v6")
    for f in sorted(os.listdir(pasta)):
        if not f.endswith(".md") or f.startswith("_"): continue
        t = open(os.path.join(pasta, f), encoding="utf-8").read()
        m = re.search(r"^cap:\s*(\d+)", t, re.M)
        if not m: continue
        nn, sem_capa = f"{int(m.group(1)):02d}", re.search(r"^capa:\s*n[aã]o", t, re.M)
        blocos = [(tp, (tt or "").strip()) for tp, tt in re.findall(r"^=== (\w+)(?:\s*\|\s*(.*))?$", t, re.M) if tp != "validar"]
        for k, (tp, tt) in enumerate(blocos, 1):
            sid = "fim" if tp == "contracapa" else (f"cap{nn}" if sem_capa and k == 1 else f"cap{nn}-{k}")
            if tt: out[sid] = tt
    out.pop("fim", None)
    return out


TIT_MD = {}


def titulo(cls, h):
    c = cls.split()
    if "capa-guia" in c: return "Capa do guia"
    if "contracapa" in c: return "Contracapa"
    m = re.search(r"<h[12][^>]*>(.*?)</h[12]>", h, re.S)
    t = limpa(m.group(1)) if m else ""
    if "capa" in c or "prefacio" in c: return "Abertura: " + t
    return t


def confere_notas(guia):
    """As notas vêm do HTML (para saber a página); o total por capítulo tem que bater com os blocos === validar."""
    ult = max(int(s["cap"]) for s in guia["slides"])
    md = {}
    pasta = os.path.join(R, "conteudo-v6")
    for f in sorted(os.listdir(pasta)):
        if not f.endswith(".md") or f.startswith("_"): continue
        t = open(os.path.join(pasta, f), encoding="utf-8").read()
        m = re.search(r"^cap:\s*(\d+)", t, re.M)
        if m: md[f"{int(m.group(1)):02d}"] = len(re.findall(r"^=== validar\s*$", t, re.M))
    ht = {}
    for s in guia["slides"]: ht[s["cap"]] = ht.get(s["cap"], 0) + len(s["notas"])
    for cap in sorted(set(md) | set(ht)):
        if md.get(cap, 0) != ht.get(cap, 0):
            print(f"  aviso: capítulo {cap} tem {md.get(cap, 0)} blocos validar no conteudo-v6 e {ht.get(cap, 0)} no index.html (rode o livro.py de novo)")
    return ult


def monta_etapas(guia):
    ult = f"{confere_notas(guia):02d}"
    usados = set()
    for e in ETAPAS:
        caps = [ult if c == "FIM" else c for c in e["caps"]]
        e["capsr"] = caps
        e["slides"] = [s for s in guia["slides"] if s["cap"] in caps]
        if not e["slides"]: sys.exit(f"etapa {e['n']} ficou sem slides: confira ETAPAS[].caps")
        usados |= {s["pg"] for s in e["slides"]}
        e["de"], e["ate"] = e["slides"][0]["pg"], e["slides"][-1]["pg"]
        grupos = []
        for s in e["slides"]:
            if not grupos or grupos[-1]["cap"] != s["cap"]:
                chave = "FIM" if s["cap"] == ult else s["cap"]
                nome = NOME_CAP.get(chave) or re.sub(r"^\d+\.\s*", "", s["cap_nome"])
                grupos.append(dict(cap=s["cap"], num="" if chave in NOME_CAP else str(int(s["cap"])), nome=nome,
                                   de=s["pg"], ate=s["pg"], id=s["id"]))
            grupos[-1]["ate"] = s["pg"]
        e["grupos"] = grupos
        e["notas"] = [dict(pg=s["pg"], id=s["id"], titulo=s["titulo"], texto=n) for s in e["slides"] for n in s["notas"]]
    fora = [s["pg"] for s in guia["slides"] if s["pg"] not in usados]
    if fora: print("  aviso: páginas fora de qualquer etapa:", fora)
    for e in ETAPAS:
        nn = len(e["notas"])
        print(f"  etapa {e['n']} · {e['nome']}: páginas {e['de']} a {e['ate']} ({len(e['slides'])} slides, {nn} nota{'' if nn == 1 else 's'})")


# ---------------------------------------------------------------- miniaturas
def porta_livre():
    with socket.socket() as so:
        so.bind(("127.0.0.1", 0)); return so.getsockname()[1]


def miniaturas(total, perfil=None, largura=480):
    import fitz
    from PIL import Image
    chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if not os.path.exists(chrome): print("  Chrome não encontrado: miniaturas mantidas"); return
    tmp = tempfile.mkdtemp(prefix="etapas-")
    perfil = perfil or os.path.join(tmp, "perfil")
    pdf = os.path.join(tmp, "guia.pdf")
    porta = porta_livre()
    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(porta), "--bind", "127.0.0.1", "--directory", R],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(1.0)
        ch = subprocess.Popen([chrome, "--headless=new", "--disable-gpu", "--no-first-run", f"--user-data-dir={perfil}",
                               "--run-all-compositor-stages-before-draw", "--virtual-time-budget=25000",
                               "--no-pdf-header-footer", f"--print-to-pdf={pdf}",
                               f"http://127.0.0.1:{porta}/index.html?mini={int(time.time())}"],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        t0 = time.time()
        while time.time() - t0 < 180:
            if ch.poll() is not None: break
            if os.path.exists(pdf) and os.path.getsize(pdf) > 0:
                time.sleep(3); break
            time.sleep(1)
        if ch.poll() is None: ch.kill()
    finally:
        srv.terminate()
    if not (os.path.exists(pdf) and os.path.getsize(pdf) > 0):
        print("  o Chrome não gerou o PDF: miniaturas mantidas"); return
    d = fitz.open(pdf)
    if d.page_count != total:
        print(f"  aviso: o PDF tem {d.page_count} páginas e o guia tem {total} slides")
    out = os.path.join(R, "aprovacao", "miniaturas"); os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        if re.match(r"p\d+\.webp$", f): os.remove(os.path.join(out, f))
    for i, pg in enumerate(d, 1):
        z = largura * 2 / pg.rect.width
        pm = pg.get_pixmap(matrix=fitz.Matrix(z, z))
        im = Image.frombytes("RGB", (pm.width, pm.height), pm.samples)
        im = im.resize((largura, round(pm.height * largura / pm.width)), Image.LANCZOS)
        im.save(os.path.join(out, nome_mini(i)), "WEBP", quality=80, method=6)
    print(f"  {d.page_count} miniaturas em aprovacao/miniaturas/")
    shutil.rmtree(tmp, ignore_errors=True)


def nome_mini(pg): return f"p{pg:02d}.webp"


# ---------------------------------------------------------------- pacotes por etapa
CSS_PACOTE = r"""
/* ===== pacote de aprovação (gerado por tools/v6/etapas.py) ===== */
.ap-barra{position:fixed;top:0;left:0;right:0;height:40px;z-index:40;display:flex;align-items:center;gap:14px;padding:0 14px;background:#06182f;color:rgba(255,255,255,.82);font:500 13.5px/1 var(--f-txt);border-bottom:1px solid rgba(32,213,242,.28)}
.ap-barra a{color:inherit;text-decoration:none;white-space:nowrap}
.ap-volta{display:inline-flex;align-items:center;gap:7px;font-weight:600;height:28px;padding:0 13px 0 10px;border-radius:0 14px 14px 14px;background:var(--verde);color:var(--navy)!important}
.ap-volta:hover{background:#13c238}
.ap-et{flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ap-et b{color:#fff;font-weight:600}
.ap-et i{font:700 19px/1 var(--f-mao);color:var(--ciano);font-style:normal;margin-left:4px}
.ap-guia{opacity:.7}.ap-guia:hover{opacity:1}
@media (max-width:640px){.ap-nm,.ap-guia-l{display:none}.ap-barra{gap:10px}}
@media (max-width:400px){.ap-et i{display:none}}
@media screen{
 .paisagem .rolo{top:40px}
 .retrato .rolo{position:fixed;top:40px;left:0;right:0;bottom:0;height:auto;margin:0}
 .retrato .slide,.retrato .lv{min-height:calc(100svh - 104px)}
}
@media print{.ap-barra{display:none!important}}
.indice a.fora{opacity:.5}
.indice .ap-ind-n{margin:14px 0 4px;font-size:13px;line-height:1.45;color:#6B7585}
.indice .ap-ind{display:block;font:700 22px/1.1 var(--f-mao);color:var(--verde);margin:-6px 0 12px}

/* slide de abertura da etapa */
.ap-slide{background:#fff}
.ap-l{left:0;top:0;bottom:0;width:640px;background:var(--navy);color:#fff;padding:84px 96px 70px 96px;box-sizing:border-box;display:flex;flex-direction:column}
.ap-slide .ap-kick{font:700 36px/1 var(--f-mao);color:var(--ciano);transform:rotate(-1.5deg);transform-origin:left;margin:0 0 6px}
.ap-slide .ap-n{display:flex;align-items:baseline;gap:14px;margin:0;font-family:var(--f-tit)}
.ap-n span{font:400 30px/1 var(--f-tit);color:rgba(255,255,255,.7)}
.ap-n b{font:400 200px/.9 var(--f-tit);color:var(--verde);font-weight:400}
.ap-n small{font:500 22px/1 var(--f-txt);color:rgba(255,255,255,.7)}
.ap-tit{font:400 54px/1.06 var(--f-tit);margin:18px 0 14px;max-width:11ch}
.ap-slide .ap-pg{font-size:19px;line-height:1.4;margin:0;color:rgba(255,255,255,.78)}
.ap-pg b{color:#fff;font-weight:600}
.ap-datas{margin:auto 0 0;padding:0;list-style:none;display:grid;gap:0;position:relative}
.ap-datas li{display:grid;grid-template-columns:26px 1fr auto;align-items:center;gap:14px;padding:11px 0;border-top:1px solid rgba(255,255,255,.14);font-size:16px}
.ap-datas li:last-child{border-bottom:1px solid rgba(255,255,255,.14)}
.ap-datas i{width:14px;height:14px;border-radius:50%;background:var(--verde);justify-self:center}
.ap-datas li:nth-child(2) i{background:transparent;box-shadow:inset 0 0 0 3px var(--ciano)}
.ap-datas li:nth-child(3) i{border-radius:3px;transform:rotate(45deg);background:#fff}
.ap-datas span{color:rgba(255,255,255,.72)}
.ap-datas b{font-weight:600;white-space:nowrap}
.ap-geo{position:absolute;right:0;top:0;bottom:0;width:58px;overflow:hidden}
.ap-geo svg{width:100%;height:100%}
.ap-geo .b{fill:var(--azul)}.ap-geo .a{fill:var(--verde)}
.ap-r{left:720px;right:96px;top:96px;bottom:84px;display:flex;flex-direction:column}
.ap-h{font:400 46px/1.1 var(--f-tit);margin:0 0 18px;color:var(--navy)}
.ap-h3{font:600 15px/1 var(--f-txt);letter-spacing:.12em;text-transform:uppercase;color:#0A7F23;margin:38px 0 16px}
.ap-caps{list-style:none;margin:0;padding:0;border-top:1.5px solid var(--navy)}
.ap-caps a{display:grid;grid-template-columns:40px 1fr auto;gap:14px;align-items:center;padding:15px 0;border-bottom:1px solid #D5D9DF;color:var(--navy);text-decoration:none;font-size:21px;line-height:1.3}
.ap-caps a:hover .ap-cn{color:var(--azul)}
.ap-caps .ap-num{width:36px;height:36px;border-radius:50%;background:var(--verde);color:var(--navy);display:grid;place-items:center;font:400 18px/1 var(--f-tit)}
.ap-caps .ap-num.vazio{background:#E7EAEE}
.ap-caps em{font-style:normal;font-size:15px;color:#5B677A;white-space:nowrap}
.ap-conf{list-style:none;margin:0;padding:0;display:grid;gap:14px}
.ap-conf li{display:grid;grid-template-columns:28px 1fr;gap:12px;font-size:19px;line-height:1.42;color:#24344F}
.ap-conf li::before{content:"";width:20px;height:20px;margin-top:3px;border-radius:0 7px 7px 7px;box-shadow:inset 0 0 0 2px var(--verde)}
.ap-slide .ap-nota{margin:auto 0 0;padding:16px 20px;background:#F1F2F3;border-radius:0 16px 16px 16px;font-size:16.5px;line-height:1.45;color:#3A4A63}
.ap-nota b{color:var(--navy);font-weight:600}
.ap-r-mark{display:inline-grid;place-items:center;min-width:22px;height:22px;padding:0 6px;border-radius:11px;background:var(--amarelo);color:var(--navy);font:700 12px/1 var(--f-txt);vertical-align:2px}

/* slide final: como aprovar */
.ap-q{left:96px;top:92px;width:760px;bottom:80px;display:flex;flex-direction:column}
.ap-q .kick{margin-bottom:10px}
.ap-q .h2{font:400 56px/1.06 var(--f-tit);margin:0 0 30px}
.ap-passos{list-style:none;margin:0;padding:0;display:grid;gap:30px;counter-reset:p}
.ap-passos li{display:grid;grid-template-columns:58px 1fr;gap:18px;align-items:start}
.ap-passos li>span{width:52px;height:52px;border-radius:50%;display:grid;place-items:center;font:400 26px/1 var(--f-tit);background:var(--verde);color:var(--navy)}
.ap-passos li:nth-child(2)>span{background:var(--azul);color:#fff}
.ap-passos li:nth-child(3)>span{background:var(--navy);color:#fff}
.ap-passos b{display:block;font:600 23px/1.25 var(--f-txt);margin:6px 0 6px}
.ap-slide .ap-passos p{margin:0;font-size:18.5px;line-height:1.48;color:#3A4A63}
.ap-q .bt{align-self:flex-start;margin-top:auto}
.ap-v{left:930px;right:96px;top:92px;bottom:80px;background:var(--amarelo);color:#3a2d00;border-radius:0 28px 28px 28px;padding:30px 34px;box-sizing:border-box;overflow:hidden;font-size:calc(19px * var(--fit,1))}
.ap-v h3{font:400 1.75em/1.12 var(--f-tit);color:var(--navy);margin:0 0 .35em}
.ap-slide .ap-v>p{margin:0 0 1em;font-size:.95em;line-height:1.45}
.ap-v ol{list-style:none;margin:0;padding:0;display:grid;gap:.85em}
.ap-v li{display:grid;grid-template-columns:auto 1fr;gap:.75em;line-height:1.45}
.ap-v li a{align-self:start;background:var(--navy);color:#fff;text-decoration:none;font:600 .8em/1 var(--f-txt);padding:.45em .65em;border-radius:0 .7em .7em .7em;white-space:nowrap;margin-top:.1em}
.ap-v .ap-vazio{font-size:1.05em;line-height:1.5}

@media screen{
 .retrato .ap-l{margin:-18px -20px 22px!important;padding:26px 20px 22px!important;display:block}
 .retrato .ap-slide .ap-kick{font-size:26px}
 .retrato .ap-n b{font-size:110px}
 .retrato .ap-n span{font-size:22px}
 .retrato .ap-n small{font-size:16px}
 .retrato .ap-tit{font-size:34px;margin:12px 0 10px}
 .retrato .ap-slide .ap-pg{font-size:15.5px;margin-bottom:18px}
 .retrato .ap-datas li{font-size:14.5px;grid-template-columns:20px 1fr auto;gap:10px}
 .retrato .ap-geo{display:none}
 .retrato .ap-h{font-size:28px}
 .retrato .ap-h3{margin-top:22px}
 .retrato .ap-caps a{padding:11px 0;font-size:16px;grid-template-columns:34px 1fr auto;gap:10px}
 .retrato .ap-caps .ap-num{width:30px;height:30px;font-size:15px}
 .retrato .ap-caps em{font-size:13px}
 .retrato .ap-conf li{font-size:15.5px}
 .retrato .ap-h3{font-size:13px}
 .retrato .ap-slide .ap-nota{margin-top:20px;font-size:14.5px}
 .retrato .ap-q .h2{font-size:30px;margin-bottom:18px}
 .retrato .ap-passos li{grid-template-columns:44px 1fr;gap:12px}
 .retrato .ap-passos li>span{width:40px;height:40px;font-size:20px}
 .retrato .ap-passos b{font-size:17px}
 .retrato .ap-slide .ap-passos p{font-size:15px}
 .retrato .ap-q .bt{margin-top:20px}
 .retrato .ap-v{padding:20px 18px!important;border-radius:0 20px 20px 20px!important;font-size:15px!important}
}
"""

GEO = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="448.5 -9.1 126.5 1339.7" preserveAspectRatio="xMidYMin slice">{}</svg>')


def geo_paths():
    f = os.path.join(R, "assets", "marca", "elementos", "animais-faixa.svg")
    try:
        t = open(f, encoding="utf-8").read()
        return "".join(re.findall(r"<path[^>]*/>", t))
    except OSError:
        return ""


def slide_abertura(e, n_tot):
    caps = "".join(
        f'<li><a href="#{g["id"]}"><span class="ap-num{"" if g["num"] else " vazio"}">{g["num"]}</span>'
        f'<span class="ap-cn">{esc(g["nome"])}</span><em>{"p. " + str(g["de"]) if g["de"] == g["ate"] else "p. %d a %d" % (g["de"], g["ate"])}</em></a></li>'
        for g in e["grupos"])
    conf = "".join(f"<li>{esc(c)}</li>" for c in e["conferir"])
    nn = len(e["notas"])
    nota_r = (f'O botão <span class="ap-r-mark">R</span> lá embaixo mostra, em amarelo, os <b>{nn} pontos para a Ourofino validar</b> nas próprias páginas.'
              if nn else "Esta etapa não tem pontos abertos para validar.")
    ret = f'até {dsem(e["retorno"])}'
    return (f'<section class="slide pg-impar lv ap-slide ap-abre" id="etapa" data-cap="E" data-cap-nome="Etapa {e["n"]} de {n_tot} · para aprovação">'
            f'<div class="ap-l z"><p class="ap-kick">para aprovação</p>'
            f'<p class="ap-n"><span>etapa</span><b>{e["n"]}</b><small>de {n_tot}</small></p>'
            f'<h1 class="ap-tit">{esc(e["nome"])}</h1>'
            f'<p class="ap-pg">Páginas <b>{e["de"]} a {e["ate"]}</b> do guia completo · {len(e["slides"])} páginas</p>'
            f'<ul class="ap-datas"><li><i></i><span>Envio da 75 LAB</span><b>{dsem(e["envio"])}</b></li>'
            f'<li><i></i><span>Retorno da Ourofino</span><b>{ret}</b></li>'
            f'<li><i></i><span>Check no touchpoint</span><b>{dsem(e["check"])}</b></li></ul>'
            f'<div class="ap-geo" aria-hidden="true">{GEO.format(geo_paths())}</div></div>'
            f'<div class="ap-r z"><h2 class="ap-h">Nesta etapa</h2><ol class="ap-caps">{caps}</ol>'
            f'<h3 class="ap-h3">O que conferir</h3><ul class="ap-conf">{conf}</ul>'
            f'<p class="ap-nota">Os números das páginas são os mesmos do guia completo: anote a página em cada ajuste. {nota_r}</p></div>'
            f'</section>\n')


def slide_aprovar(e, n_tot):
    if e["notas"]:
        itens = "".join(f'<li><a href="#{n["id"]}">p. {n["pg"]}</a><span>{esc(n["texto"])}</span></li>' for n in e["notas"])
        v = (f'<h3>Para a Ourofino validar</h3><p>{len(e["notas"])} {"ponto" if len(e["notas"]) == 1 else "pontos"} desta etapa. '
             f'Responda junto com o retorno.</p><ol>{itens}</ol>')
    else:
        v = '<h3>Para a Ourofino validar</h3><p class="ap-vazio">Esta etapa não tem pontos abertos. Basta conferir as páginas.</p>'
    return (f'<section class="slide pg-par lv ap-slide ap-fim t-papel" id="aprovar" data-cap="E" data-cap-nome="Etapa {e["n"]} de {n_tot} · como aprovar">'
            f'<div class="ap-q z"><span class="kick">para fechar a etapa</span><h2 class="h2">Como aprovar esta etapa</h2>'
            f'<ol class="ap-passos">'
            f'<li><span>1</span><div><b>Passe por todas as páginas</b><p>No computador, use as setas ou o teclado. No celular, role a tela para baixo.</p></div></li>'
            f'<li><span>2</span><div><b>Anote a página de cada ajuste</b><p>O número aparece no canto da página e no contador lá embaixo, igual ao do guia completo.</p></div></li>'
            f'<li><span>3</span><div><b>Responda no cronograma</b><p>Abra “Dar o retorno desta etapa”, marque Aprovada, Aprovada com ajustes ou Refazer e toque em Copiar retorno. Depois é só colar no e-mail ou no WhatsApp.</p></div></li>'
            f'</ol><a class="bt" href="../../cronograma/#retorno-{e["n"]}">Dar o retorno no cronograma</a></div>'
            f'<div class="ap-v z" data-fit>{v}</div></section>\n')


def pacote(e, guia, n_tot):
    corpo = slide_abertura(e, n_tot)
    for s in e["slides"]:
        corpo += s["html"].replace('<section class="slide ', f'<section data-pg="{s["pg"]}" class="slide ', 1)
    corpo += slide_aprovar(e, n_tot)
    ids = set(re.findall(r'\bid="([^"]+)"', corpo))
    head, cauda = guia["head"], guia["cauda"]

    def links(t):
        def troca(m):
            alvo = m.group(1)
            if alvo in ids: return m.group(0)
            return f'href="../../#{alvo}" target="_blank" rel="noopener"'
        return re.sub(r'href="#([^"]+)"', troca, t)

    def assets(t): return re.sub(r'(?<![\w./-])assets/', '../../assets/', t)

    corpo = assets(links(corpo))
    cauda = assets(links(cauda))
    cauda = re.sub(r'(<a href="\.\./\.\./#[^"]+" target="_blank" rel="noopener")( data-cap="[^"]*")', r'\1 class="fora"\2', cauda)
    cauda = cauda.replace("<h3>Índice</h3>", f'<h3>Índice</h3><span class="ap-ind">nesta etapa: {esc(e["nome"])}</span>', 1)
    cauda = re.sub(r'</ol>(<a class="ind-tr")', r'</ol><p class="ap-ind-n">Em cinza, os capítulos de outras etapas: eles abrem no guia completo, numa nova aba.</p>\1', cauda, 1)
    head = assets(head)
    head = re.sub(r"<title>[^<]*</title>", f"<title>Etapa {e['n']} de {n_tot} · Guia de Execução no PDV · Ourofino Pet</title>", head, 1)
    head = head.replace("</head>", f'<meta name="robots" content="noindex">\n<style>{CSS_PACOTE}</style>\n</head>', 1)
    barra = (f'<div class="ap-barra"><a class="ap-volta" href="../../cronograma/#etapa-{e["n"]}">← <span>Cronograma</span></a>'
             f'<span class="ap-et"><b>Etapa {e["n"]} de {n_tot}</b><span class="ap-nm"> · {esc(e["nome"])}</span> <i>para aprovação</i></span>'
             f'<a class="ap-guia" href="../../" target="_blank" rel="noopener"><span class="ap-guia-l">Guia completo </span>↗</a></div>\n')
    head = head.replace('<body>\n<div class="rolo">', '<body class="pacote">\n' + barra + '<div class="rolo">', 1)
    if 'class="pacote"' not in head: sys.exit("não achei <body> seguido de .rolo no index.html")
    nn = len(e["notas"])
    trocas = [
        ('if (p) p.textContent = i + 1;', 'if (p) p.textContent = s.getAttribute("data-pg") || "";'),
        ('cont.textContent = (i + 1) + " / " + total;',
         'cont.textContent = (s.getAttribute("data-pg") ? "p. " + s.getAttribute("data-pg") + " · " : "") + (i + 1) + "/" + total;'),
        ('livreH = innerHeight - 64', 'livreH = innerHeight - 104'),
    ]
    for a, b in trocas:
        if a not in cauda: sys.exit(f"o motor mudou: não achei {a!r}")
        cauda = cauda.replace(a, b, 1)
    cauda = re.sub(r'title="Mostrar as \d+ notas para a Ourofino validar"',
                   f'title="Mostrar {"as " + str(nn) + " notas" if nn != 1 else "a nota"} desta etapa para a Ourofino validar"', cauda, 1)
    out = os.path.join(R, "aprovacao", f"etapa-{e['n']}")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "index.html"), "w", encoding="utf-8") as f:
        f.write(head + "\n" + assets(links(guia["prefixo"])) + corpo + cauda)


# ---------------------------------------------------------------- cronograma
def pos(d):
    d = D(d) if isinstance(d, str) else d
    return (d - G_INI).days / ((G_FIM - G_INI).days + 1) * 100


def gantt():
    dias = (G_FIM - G_INI).days + 1
    meses, d = [], G_INI
    while d <= G_FIM:
        ini = d
        while d <= G_FIM and d.month == ini.month: d += dt.timedelta(days=1)
        meses.append((ini, d))
    cab = "".join(f'<span class="gm" style="left:{pos(a):.3f}%;width:{pos(b) - pos(a):.3f}%">{MESES[a.month - 1]}</span>' for a, b in meses)
    sem, d = "", G_INI
    while d <= G_FIM:
        sem += f'<span class="gs" style="left:{pos(d):.3f}%">{d.day}</span>'
        d += dt.timedelta(days=7)
    grade, d = "", G_INI
    while d <= G_FIM:
        grade += f'<i style="left:{pos(d):.3f}%"></i>'
        d += dt.timedelta(days=7)
    faixas = ""
    for a, b, nome, sub in PAUSAS:
        faixas += (f'<div class="gp" style="left:{pos(a):.3f}%;width:{pos(D(b) + dt.timedelta(days=1)) - pos(a):.3f}%">'
                   f'<span><b>{nome}</b>{(" · " + sub) if sub and nome != "Carnaval" else ""}</span></div>')
    faixas += (f'<div class="gp gc" style="left:{pos(CONVENCAO[0]):.3f}%;width:{pos(D(CONVENCAO[1]) + dt.timedelta(days=1)) - pos(CONVENCAO[0]):.3f}%">'
               f'<span><b>Convenção</b></span></div>')
    faixas += f'<div class="ge" style="left:{pos(D(ENTREGA)) + 50 / dias:.3f}%"><span>Entrega 19/02</span></div>'
    meio = 50 / dias

    def linha(rot, sub, cor, tinta, envio, ret, check, extra="", ancora=""):
        b = (f'<i class="gb-e" style="left:{pos(envio) + meio:.3f}%"></i>'
             f'<span class="gb" style="left:{pos(envio) + meio:.3f}%;width:{pos(ret) - pos(envio):.3f}%;--c:{cor}"></span>')
        if check:
            b += (f'<i class="gb-c" style="left:{pos(check) + meio:.3f}%;--c:{cor}"></i>'
                  f'<span class="gb-t" style="left:{pos(check) + meio:.3f}%">check {dm(check)}</span>')
        b += extra
        return (f'<div class="gr"><a class="gl" href="#{ancora}"><b style="--c:{cor};--t:{tinta}">{rot}</b><span>{esc(sub)}</span></a>'
                f'<div class="gt">{b}</div></div>')

    linhas = "".join(linha(str(e["n"]), e["nome"], e["cor"], e["tinta"], e["envio"], e["retorno"], e["check"], ancora=f"etapa-{e['n']}") for e in ETAPAS)
    a, b = FINAIS
    linhas += linha(a["k"], a["nome"], a["cor"], a["tinta"], a["envio"], a["retorno"], a["check"], ancora="reta-final")
    extra_b = (f'<span class="gb-t gb-t2" style="left:{pos(b["retorno"]) + meio:.3f}%">aprovação {dm(b["retorno"])}</span>')
    linhas += linha(b["k"], b["nome"], b["cor"], b["tinta"], b["envio"], b["retorno"], None, extra_b, ancora="reta-final")
    return (f'<div class="gantt" data-ini="{G_INI.isoformat()}" data-dias="{dias}">'
            f'<div class="gh"><div class="gl gl-h"></div><div class="gt gt-h"><div class="gms">{cab}</div><div class="gss">{sem}</div></div></div>'
            f'<div class="gcorpo"><div class="gfundo"><div class="gl"></div><div class="gt">{grade}{faixas}<div class="gh-hoje" hidden><span>hoje</span></div></div></div>'
            f'{linhas}</div></div>')


def eventos():
    ev = {}
    def add(d, tipo, txt, cor=None): ev.setdefault(d, []).append((tipo, txt, cor))
    for e in ETAPAS:
        add(e["envio"], "envio", f"Envio da etapa {e['n']}: {e['nome']}", e["cor"])
        add(e["retorno"], "retorno", f"Retorno da Ourofino sobre a etapa {e['n']}", e["cor"])
        add(e["check"], "check", f"Check da etapa {e['n']}", e["cor"])
    a, b = FINAIS
    add(a["envio"], "envio", "Envio do guia completo, com todos os ajustes", a["cor"])
    add(a["retorno"], "retorno", "Retorno da Ourofino sobre o guia completo", a["cor"])
    add(a["check"], "check", "Check do guia completo", a["cor"])
    add(b["envio"], "envio", "Envio da arte final: PDF de impressão e versão digital", b["cor"])
    add(b["retorno"], "aprov", "Aprovação final da arte", b["cor"])
    add(ENTREGA, "marco", "Entrega oficial do guia", "#10AD31")
    lis = []
    pausas = {p[0]: p for p in PAUSAS}
    datas = sorted(set(ev) | set(pausas))
    for d in datas:
        if d in pausas:
            a_, b_, nome, sub = pausas[d]
            txt = f"{nome}: sem envios até {dm(b_)}" if sub == "sem envios" else f"{nome} ({sub})"
            lis.append(f'<li class="tl-i tl-pausa"><time><b>{dm(a_)}</b><span>a {dm(b_)}</span></time><div><p>{esc(txt)}</p></div></li>')
            if d not in ev: continue
        itens = ev[d]
        tp = any(t == "check" for t, _, _ in itens)
        tipos = [t for t, _, _ in itens]
        tipo = next((t for t in ("marco", "check", "aprov") if t in tipos), tipos[0])
        cor = next((c for t, _, c in itens if t == tipo), itens[0][2])
        tit = "Touchpoint" if tp else ""
        ps = "".join(f"<p>{esc(x)}</p>" for _, x, _ in itens)
        lis.append(f'<li class="tl-i tl-{tipo}" style="--c:{cor}" data-d="{d}"><time><b>{dm(d)}</b><span>{DIAS[D(d).weekday()]}</span></time>'
                   f'<div>{"<strong>" + tit + "</strong>" if tit else ""}{ps}</div></li>')
    lis.append('<li class="tl-i tl-marco tl-conv"><time><b>mar</b><span>1ª semana</span></time><div><strong>Convenção</strong><p>Guia pronto, impresso e digital</p></div></li>')
    return '<ol class="tl">' + "".join(lis) + "</ol>"


def card_etapa(e, n_tot):
    caps = "".join(f'<li><span class="ec-n{"" if g["num"] else " vazio"}">{g["num"]}</span><span>{esc(g["nome"])}</span>'
                   f'<em>{"p. " + str(g["de"]) if g["de"] == g["ate"] else "p. %d a %d" % (g["de"], g["ate"])}</em></li>' for g in e["grupos"])
    pkg = f"../aprovacao/etapa-{e['n']}/"
    datas = (f'<ol class="ed"><li><i class="ed-e"></i><span>Envio da 75 LAB</span><b>{dsem(e["envio"])}</b></li>'
             f'<li><i class="ed-r"></i><span>Retorno da Ourofino</span><b>até {dsem(e["retorno"])}</b>'
             f'{"<small>" + esc(e["nota_retorno"]) + "</small>" if e.get("nota_retorno") else ""}</li>'
             f'<li><i class="ed-c"></i><span>Check no touchpoint</span><b>{dsem(e["check"])}</b></li></ol>')
    conf = "".join(f"<li>{esc(c)}</li>" for c in e["conferir"])
    if e["notas"]:
        val = "".join(f'<li><a href="{pkg}#{n["id"]}">p. {n["pg"]}</a><span>{esc(n["texto"])}</span></li>' for n in e["notas"])
        val = f'<ul class="ev">{val}</ul>'
    else:
        val = '<p class="ev-vazio">Nenhum ponto aberto nesta etapa.</p>'
    prec = ""
    if e["precisa"]:
        prec = ('<section class="eb eb-prec"><h4>Precisamos da Ourofino</h4><ul class="ep">' +
                "".join(f'<li><b>até {dsem(d)}</b><span>{esc(t)}</span></li>' for d, t in e["precisa"]) + "</ul></section>")
    th = "".join(f'<a class="th" href="{pkg}#{s["id"]}"><span class="th-i"><img src="../aprovacao/miniaturas/{nome_mini(s["pg"])}" '
                 f'width="480" height="270" loading="lazy" alt=""></span><span class="th-p">p. {s["pg"]}</span>'
                 f'<span class="th-t">{esc(s["titulo"])}</span></a>' for s in e["slides"])
    return (f'<article class="et" id="etapa-{e["n"]}" style="--c:{e["cor"]};--t:{e["tinta"]}" data-envio="{e["envio"]}" data-check="{e["check"]}">'
            f'<header class="et-cab"><div class="et-num"><span>etapa</span><b>{e["n"]}</b><small>de {n_tot}</small></div>'
            f'<div class="et-tt"><p class="et-pg">páginas {e["de"]} a {e["ate"]} · {len(e["slides"])} páginas</p><h3>{esc(e["nome"])}</h3></div>'
            f'<ul class="ec">{caps}</ul><span class="et-agora" hidden>nesta semana</span></header>'
            f'{datas}'
            f'<div class="eg{" eg3" if prec else ""}"><section class="eb"><h4>O que conferir</h4><ul class="eo">{conf}</ul></section>'
            f'<section class="eb eb-val"><h4>Para a Ourofino validar <span>{len(e["notas"])}</span></h4>{val}</section>{prec}</div>'
            f'<div class="et-th"><div class="et-th-cab"><h4>As páginas desta etapa</h4><span>toque numa página para abrir</span></div><div class="ths">{th}</div></div>'
            f'<div class="et-ac"><a class="btn" href="{pkg}">Abrir a etapa para aprovar <span aria-hidden="true">→</span></a></div>'
            f'{bloco_retorno(e)}</article>')


def bloco_retorno(e):
    val = ""
    if e["notas"]:
        val = ('<div class="rt-val"><p class="rt-l">Respostas aos pontos para validar <small>(opcional)</small></p>' +
               "".join(f'<label class="rt-vi"><span><b>p. {n["pg"]}</b> {esc(n["texto"][:140] + ("…" if len(n["texto"]) > 140 else ""))}</span>'
                       f'<textarea rows="2" data-val="{i}" placeholder="Resposta da Ourofino"></textarea></label>' for i, n in enumerate(e["notas"])) +
               "</div>")
    n = e["n"]
    return (f'<details class="rt" id="retorno-{n}" data-etapa="{n}"><summary><span>Como dar o retorno</span><small>marque, comente por página e copie o texto</small></summary>'
            f'<div class="rt-in">'
            f'<fieldset class="rt-sit"><legend class="rt-l">Como fica esta etapa?</legend>'
            f'<label><input type="radio" name="sit-{n}" value="Aprovada"><span><i></i>Aprovada</span></label>'
            f'<label><input type="radio" name="sit-{n}" value="Aprovada com ajustes"><span><i></i>Aprovada com ajustes</span></label>'
            f'<label><input type="radio" name="sit-{n}" value="Refazer"><span><i></i>Refazer</span></label></fieldset>'
            f'<div class="rt-pgs"><p class="rt-l">Ajustes por página</p><div class="rt-linhas" data-linhas></div>'
            f'<button type="button" class="rt-mais" data-mais>+ ajuste em outra página</button></div>'
            f'{val}'
            f'<label class="rt-geral"><span class="rt-l">Comentário geral <small>(opcional)</small></span><textarea rows="3" data-geral placeholder="O que vale para a etapa toda"></textarea></label>'
            f'<div class="rt-prev"><p class="rt-l">Texto que vai ser copiado</p><textarea readonly rows="7" data-previa></textarea></div>'
            f'<div class="rt-ac"><button type="button" class="btn" data-copia>Copiar retorno</button><span class="rt-ok" data-ok role="status"></span>'
            f'<button type="button" class="rt-limpa" data-limpa>Apagar rascunho</button></div>'
            f'<p class="rt-obs">O rascunho fica salvo só neste aparelho, até você copiar e mandar.</p></div></details>')


def card_final(f):
    datas = (f'<ol class="ed"><li><i class="ed-e"></i><span>Envio da 75 LAB</span><b>{dsem(f["envio"])}</b></li>'
             f'<li><i class="ed-r"></i><span>{"Retorno da Ourofino" if f["check"] else "Aprovação final"}</span><b>até {dsem(f["retorno"])}</b></li>')
    datas += (f'<li><i class="ed-c"></i><span>Check no touchpoint</span><b>{dsem(f["check"])}</b></li>' if f["check"]
              else f'<li><i class="ed-m"></i><span>Entrega oficial</span><b>{dsem(ENTREGA)}</b></li>') + "</ol>"
    conf = "".join(f"<li>{esc(c)}</li>" for c in f["conferir"])
    prec = ""
    if f["precisa"]:
        prec = ('<div class="fc-prec"><h4>Precisamos da Ourofino</h4><ul class="ep">' +
                "".join(f'<li><b>até {dsem(d)}</b><span>{esc(t)}</span></li>' for d, t in f["precisa"]) + "</ul></div>")
    return (f'<article class="fc" style="--c:{f["cor"]};--t:{f["tinta"]}"><div class="fc-k">{f["k"]}</div><h3>{esc(f["nome"])}</h3>'
            f'<p class="fc-d">{esc(f["desc"])}</p>{datas}<h4>O que conferir</h4><ul class="eo">{conf}</ul>{prec}</article>')


def pedidos():
    itens = []
    for e in ETAPAS:
        for d, t in e["precisa"]: itens.append((d, t, f"para a etapa {e['n']}", f"#etapa-{e['n']}"))
    for f in FINAIS:
        for d, t in f["precisa"]: itens.append((d, t, "para o " + f["nome"].lower(), "#reta-final"))
    itens.sort(key=lambda x: x[0])
    return "".join(f'<li data-d="{d}"><time><b>{dm(d)}</b><span>{DIAS[D(d).weekday()]}</span></time><span class="pd-t">{esc(t)}</span>'
                   f'<a href="{a}">{esc(p)}</a></li>' for d, t, p, a in itens)


def janelas():
    """Textos do selo "onde estamos" do topo, calculados no navegador pela data do dia."""
    j = [dict(de="2000-01-01", ate=(D(ETAPAS[0]["envio"]) - dt.timedelta(days=1)).isoformat(),
              txt=f"A etapa 1 sai na {dsem(ETAPAS[0]['envio'])}")]
    for e in ETAPAS:
        j.append(dict(de=e["envio"], ate=e["retorno"], txt=f"Agora: etapa {e['n']} com a Ourofino até {dsem(e['retorno'])}", n=e["n"]))
        j.append(dict(de=(D(e["retorno"]) + dt.timedelta(days=1)).isoformat(), ate=(D(e["check"]) - dt.timedelta(days=1)).isoformat(),
                      txt=f"Agora: check da etapa {e['n']} no touchpoint de {dsem(e['check'])}", n=e["n"]))
    a, b = FINAIS
    j.append(dict(de=(D(ETAPAS[-1]["check"])).isoformat(), ate=(D(a["envio"]) - dt.timedelta(days=1)).isoformat(),
                  txt=f"Próximo: o guia completo sai na {dsem(a['envio'])}"))
    j.append(dict(de=a["envio"], ate=a["retorno"], txt=f"Agora: guia completo com a Ourofino até {dsem(a['retorno'])}"))
    j.append(dict(de=(D(a["retorno"]) + dt.timedelta(days=1)).isoformat(), ate=(D(b["envio"]) - dt.timedelta(days=1)).isoformat(),
                  txt=f"Agora: check do guia completo no touchpoint de {dsem(a['check'])}"))
    j.append(dict(de=b["envio"], ate=b["retorno"], txt=f"Agora: arte final para aprovar até {dsem(b['retorno'])}"))
    j.append(dict(de=(D(b["retorno"]) + dt.timedelta(days=1)).isoformat(), ate=(D(ENTREGA) - dt.timedelta(days=1)).isoformat(),
                  txt=f"Arte final aprovada. Entrega na {dsem(ENTREGA)}"))
    j.append(dict(de=ENTREGA, ate="2099-01-01", txt=f"Guia entregue em {dm(ENTREGA)}"))
    return j


CSS_CRONO = r"""
:root{--navy:#072047;--navy-2:#0B1F45;--verde:#10AD31;--verde-esc:#0A7F23;--azul:#007CC1;--ciano:#20D5F2;--amarelo:#FFE07A;
--papel:#F5F4EF;--linha:#DCE0E6;--cinza:#5B677A;--texto:#24344F;
--f-tit:"Young Serif",Georgia,serif;--f-txt:"Poppins",Arial,sans-serif;--f-mao:"Caveat","Segoe Print",cursive}
*{box-sizing:border-box}
html{scroll-behavior:smooth;-webkit-text-size-adjust:100%}
body{margin:0;background:var(--papel);color:var(--navy);font:400 16px/1.55 var(--f-txt);-webkit-font-smoothing:antialiased}
img{max-width:100%;display:block}
a{color:inherit}
button{font:inherit;color:inherit;cursor:pointer}
.w{max-width:1160px;margin:0 auto;padding:0 16px}
@media (min-width:700px){.w{padding:0 32px}}
h1,h2,h3{font-family:var(--f-tit);font-weight:400;margin:0;letter-spacing:-.005em}
.mao{font:700 28px/1 var(--f-mao);color:var(--verde);display:inline-block;transform:rotate(-1.5deg);transform-origin:left}
:focus-visible{outline:3px solid var(--ciano);outline-offset:3px}

/* topo */
.topo{background:var(--navy-2);color:#fff;position:relative;overflow:hidden}
.topo-f{position:relative;height:62vw;max-height:440px;overflow:hidden}
.topo-f img{width:100%;height:100%;object-fit:cover;object-position:72% 50%}
.topo-f::after{content:"";position:absolute;inset:auto 0 0 0;height:40%;background:linear-gradient(to top,var(--navy-2),rgba(11,31,69,0))}
.topo-t{position:relative;padding-top:4px;padding-bottom:40px}
.topo-marcas{display:flex;align-items:center;gap:14px;margin-bottom:26px;font-size:13px;color:rgba(255,255,255,.7)}
.topo-marcas img{height:26px;width:auto}
.topo-marcas span{padding-left:14px;border-left:1px solid rgba(255,255,255,.25);line-height:1.3}
.topo .mao{color:var(--ciano);font-size:30px;margin-bottom:14px}
.topo h1{font-size:40px;line-height:1.05;max-width:14ch}
.topo .lead{font-size:17px;line-height:1.55;color:rgba(255,255,255,.82);max-width:36em;margin:16px 0 0}
.topo .lead b{color:#fff;font-weight:600}
.agora{display:inline-flex;align-items:center;gap:10px;margin-top:22px;background:var(--verde);color:var(--navy);font-weight:600;font-size:14.5px;line-height:1.3;padding:9px 16px 9px 12px;border-radius:0 18px 18px 18px}
.agora i{width:10px;height:10px;border-radius:50%;background:var(--navy);flex:none;animation:pulsa 2s ease-in-out infinite}
@keyframes pulsa{50%{transform:scale(1.5);opacity:.5}}
.fatos{list-style:none;margin:28px 0 0;padding:0;display:grid;gap:10px}
.fatos li{display:grid;grid-template-columns:auto 1fr;gap:4px 14px;align-items:baseline;padding:14px 0;border-top:1px solid rgba(255,255,255,.16)}
.fatos li:last-child{border-bottom:1px solid rgba(255,255,255,.16)}
.fatos span{font-size:12.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--ciano);font-weight:600;min-width:104px}
.fatos b{font:400 21px/1.25 var(--f-tit)}
.fatos small{grid-column:2;color:rgba(255,255,255,.7);font-size:14px}
.topo-geo{position:absolute;right:0;top:0;bottom:0;width:44px;opacity:.9;display:none}
.topo-geo svg{width:100%;height:100%}.topo-geo .b{fill:var(--azul)}.topo-geo .a{fill:var(--verde)}
@media (min-width:1180px){
 .topo{min-height:640px;display:flex;align-items:center}
 .topo-f{position:absolute;inset:0 44px 0 38%;height:auto;max-height:none}
 .topo-f img{object-position:70% 50%}
 .topo-f::after{inset:0 auto 0 0;width:46%;height:auto;background:linear-gradient(to right,var(--navy-2),rgba(11,31,69,0))}
 .topo-t{padding-top:64px;padding-bottom:64px;width:100%}
 .topo-c{max-width:560px}
 .topo h1{font-size:62px}
 .topo .lead{font-size:18px}
 .fatos{grid-template-columns:repeat(3,1fr);gap:0 24px;max-width:none}
 .fatos li{grid-template-columns:1fr;border-bottom:1px solid rgba(255,255,255,.16)}
 .fatos small{grid-column:1}
 .topo-geo{display:block}
}

/* seções */
.sec{padding-top:56px;padding-bottom:8px}
.sec-cab{margin-bottom:24px}
.sec-cab .mao{margin-bottom:10px}
.sec-cab h2{font-size:32px;line-height:1.1}
.sec-cab p{margin:10px 0 0;color:var(--cinza);max-width:44em}
@media (min-width:900px){.sec{padding-top:80px}.sec-cab h2{font-size:44px}}

/* como funciona */
.passos{list-style:none;margin:0;padding:0;display:grid;gap:14px;counter-reset:p}
.passos li{background:#fff;border-radius:0 24px 24px 24px;padding:22px 22px 22px;display:grid;grid-template-columns:52px 1fr;gap:16px;box-shadow:0 1px 0 var(--linha)}
.passos li>span{width:48px;height:48px;border-radius:50%;display:grid;place-items:center;font:400 22px/1 var(--f-tit);background:var(--verde);color:var(--navy)}
.passos li:nth-child(2)>span{background:var(--azul);color:#fff}
.passos li:nth-child(3)>span{background:var(--navy);color:#fff}
.passos small{display:block;font:700 20px/1 var(--f-mao);color:var(--verde-esc);margin-bottom:4px}
.passos b{display:block;font:600 18px/1.3 var(--f-txt);margin-bottom:6px}
.passos p{margin:0;color:var(--texto);font-size:15.5px}
@media (min-width:900px){.passos{grid-template-columns:repeat(3,1fr);gap:20px}.passos li{grid-template-columns:1fr;padding:28px}}

/* linha do tempo: Gantt no computador */
.gantt{display:none;background:#fff;border-radius:0 28px 28px 28px;padding:22px 26px 34px;box-shadow:0 1px 0 var(--linha)}
.gh,.gr,.gfundo{display:grid;grid-template-columns:230px 1fr;column-gap:18px}
.gt{position:relative}
.gt-h{height:52px}
.gms{position:relative;height:26px;border-bottom:1.5px solid var(--navy)}
.gm{position:absolute;top:0;height:26px;font:600 12px/26px var(--f-txt);letter-spacing:.12em;text-transform:uppercase;padding-left:8px;border-left:1.5px solid var(--navy)}
.gss{position:relative;height:24px}
.gs{position:absolute;top:5px;font-size:11.5px;color:var(--cinza);transform:translateX(-50%)}
.gcorpo{position:relative}
.gfundo{position:absolute;inset:0;pointer-events:none}
.gfundo .gt>i{position:absolute;top:0;bottom:0;width:1px;background:#EEF0F3}
.gp{position:absolute;top:0;bottom:0;background:repeating-linear-gradient(135deg,rgba(7,32,71,.07) 0 6px,rgba(7,32,71,0) 6px 12px);border-left:1px dashed #B9C1CC;border-right:1px dashed #B9C1CC}
.gp span{position:absolute;left:50%;top:6px;transform:translateX(-50%);white-space:nowrap;font-size:11.5px;color:var(--cinza);background:#fff;padding:2px 8px;border-radius:10px;box-shadow:0 0 0 1px var(--linha)}
.gp span b{font-weight:600;color:var(--navy)}
.gp.gc{background:rgba(16,173,49,.12);border-color:rgba(16,173,49,.6)}
.gp.gc span{top:auto;bottom:6px}
.ge{position:absolute;top:0;bottom:0;width:0;border-left:2px solid var(--verde)}
.ge span{position:absolute;top:-2px;left:6px;white-space:nowrap;background:var(--verde);color:var(--navy);font:600 11.5px/1 var(--f-txt);padding:5px 9px;border-radius:0 10px 10px 10px}
.gh-hoje{position:absolute;top:-24px;bottom:0;width:0;border-left:2px dashed var(--azul);z-index:3}
.gh-hoje span{position:absolute;bottom:-24px;left:-14px;font:700 19px/1 var(--f-mao);color:var(--azul)}
.gr{position:relative;align-items:center;min-height:54px;border-bottom:1px solid #F0F2F5}
.gr:last-child{border-bottom:0}
.gl{display:flex;align-items:center;gap:12px;text-decoration:none;color:var(--navy);font-size:14.5px;line-height:1.25;padding:6px 0}
.gl b{flex:none;width:32px;height:32px;border-radius:50%;display:grid;place-items:center;background:var(--c);color:var(--t);font:400 16px/1 var(--f-tit)}
.gl:hover span{text-decoration:underline;text-decoration-color:var(--verde);text-underline-offset:3px}
.gr .gt{height:54px}
.gb{position:absolute;top:19px;height:16px;border-radius:0 8px 8px 8px;background:var(--c);transform-origin:left;box-shadow:inset 0 0 0 1px rgba(7,32,71,.12)}
.gb-e{position:absolute;top:21px;width:12px;height:12px;margin-left:-6px;border-radius:50%;background:#fff;box-shadow:inset 0 0 0 3px var(--verde);z-index:2}
.gb-c{position:absolute;top:20px;width:14px;height:14px;margin-left:-7px;transform:rotate(45deg);background:var(--navy);box-shadow:0 0 0 2px #fff;z-index:2}
.gb-t{position:absolute;top:19px;margin-left:12px;font-size:12px;line-height:16px;color:var(--cinza);white-space:nowrap}
.gb-t2{margin-left:8px}
.g-leg{display:none;flex-wrap:wrap;gap:8px 22px;margin:14px 4px 0;font-size:13px;color:var(--cinza)}
.g-leg span{display:inline-flex;align-items:center;gap:8px}
.g-leg i{display:inline-block}
.lg-b{width:28px;height:12px;border-radius:0 6px 6px 6px;background:var(--azul)}
.lg-e{width:12px;height:12px;border-radius:50%;box-shadow:inset 0 0 0 3px var(--verde)}
.lg-c{width:11px;height:11px;transform:rotate(45deg);background:var(--navy)}
.lg-p{width:22px;height:14px;background:repeating-linear-gradient(135deg,rgba(7,32,71,.18) 0 4px,transparent 4px 8px);border:1px dashed #B9C1CC}
@media (min-width:980px){.gantt{display:block}.g-leg{display:flex}.tl{display:none}}
.js .gb{transform:scaleX(0);transition:transform .9s cubic-bezier(.2,.7,.2,1)}
.js .gantt.viu .gb{transform:none}
.js .gantt .gr:nth-child(2) .gb{transition-delay:.06s}.js .gantt .gr:nth-child(3) .gb{transition-delay:.12s}
.js .gantt .gr:nth-child(4) .gb{transition-delay:.18s}.js .gantt .gr:nth-child(5) .gb{transition-delay:.24s}
.js .gantt .gr:nth-child(6) .gb{transition-delay:.3s}.js .gantt .gr:nth-child(7) .gb{transition-delay:.36s}.js .gantt .gr:nth-child(8) .gb{transition-delay:.42s}

/* linha do tempo: trilha no celular */
.tl{list-style:none;margin:0;padding:0 0 0 4px;position:relative}
.tl::before{content:"";position:absolute;left:70px;top:14px;bottom:14px;border-left:2px dashed #B9C1CC}
.tl-i{position:relative;display:grid;grid-template-columns:56px 1fr;gap:28px;padding:10px 0}
.tl-i time{text-align:right;line-height:1.15;padding-top:4px}
.tl-i time b{display:block;font:400 18px/1.1 var(--f-tit)}
.tl-i time span{font-size:12px;color:var(--cinza)}
.tl-i>div{position:relative;background:#fff;border-radius:0 18px 18px 18px;padding:10px 14px;box-shadow:0 1px 0 var(--linha)}
.tl-i>div::before{content:"";position:absolute;left:-23px;top:13px;width:14px;height:14px;border-radius:50%;background:#fff;box-shadow:inset 0 0 0 3px var(--c,var(--verde))}
.tl-i p{margin:0;font-size:14.5px;line-height:1.4;color:var(--texto)}
.tl-i p+p{margin-top:4px}
.tl-i strong{display:block;font:700 20px/1 var(--f-mao);color:var(--verde-esc);margin-bottom:2px}
.tl-envio>div::before{background:var(--c);box-shadow:0 0 0 3px #fff}
.tl-check>div::before,.tl-aprov>div::before{border-radius:3px;transform:rotate(45deg);background:var(--navy);box-shadow:0 0 0 3px #fff;width:12px;height:12px;left:-22px}
.tl-pausa>div{background:repeating-linear-gradient(135deg,rgba(7,32,71,.06) 0 6px,transparent 6px 12px);box-shadow:inset 0 0 0 1px #CBD2DB}
.tl-pausa>div::before{background:#CBD2DB;box-shadow:0 0 0 3px var(--papel)}
.tl-marco>div{background:var(--verde)}
.tl-marco p,.tl-marco strong{color:var(--navy)}
.tl-marco>div::before{background:var(--verde);box-shadow:0 0 0 3px var(--papel)}
.tl-i.hoje>div{box-shadow:0 0 0 2px var(--azul)}
.tl-i.hoje time::after{content:attr(data-rot);display:block;font:700 18px/1 var(--f-mao);color:var(--azul);margin-top:2px}

/* cartões das etapas */
.ets{display:grid;gap:26px}
.et{background:#fff;border-radius:0 30px 30px 30px;overflow:hidden;box-shadow:0 1px 0 var(--linha),0 30px 60px -48px rgba(7,32,71,.5);scroll-margin-top:16px}
.et-cab{position:relative;display:grid;grid-template-columns:auto 1fr;gap:18px;padding:22px 20px 18px;border-top:8px solid var(--c)}
.et-num{display:flex;flex-direction:column;align-items:center;justify-content:center;width:84px;height:96px;border-radius:0 26px 26px 26px;background:var(--c);color:var(--t);line-height:1}
.et-num span{font:700 18px/1 var(--f-mao);opacity:.85}
.et-num b{font:400 44px/1 var(--f-tit);margin:8px 0 6px}
.et-num small{font-size:11px;opacity:.8}
.et-pg{margin:0 0 2px;font-size:12.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--cinza);font-weight:600}
.et h3{font-size:26px;line-height:1.1;margin-bottom:10px}
.et-tt{align-self:center}
.et h3{margin-bottom:0}
.ec{grid-column:1/-1;list-style:none;margin:0;padding:12px 0 0;display:grid;gap:6px;border-top:1px solid #EEF0F3}
.ec li{display:grid;grid-template-columns:26px 1fr auto;gap:10px;align-items:center;font-size:14.5px;line-height:1.3}
.ec-n{width:24px;height:24px;border-radius:50%;background:var(--navy);color:#fff;display:grid;place-items:center;font:400 12.5px/1 var(--f-tit)}
.ec-n.vazio{background:#E7EAEE}
.ec em{font-style:normal;font-size:12.5px;color:var(--cinza);white-space:nowrap}
.et-agora{position:absolute;right:16px;top:14px;background:var(--azul);color:#fff;font:600 12px/1 var(--f-txt);padding:7px 11px;border-radius:0 12px 12px 12px}
.ed{list-style:none;margin:0;padding:0 20px;display:grid;gap:0}
.ed li{display:grid;grid-template-columns:20px 1fr auto;column-gap:12px;align-items:center;padding:11px 0;border-top:1px solid #EEF0F3;font-size:14.5px}
.ed li span{color:var(--cinza)}
.ed li b{font-weight:600;white-space:nowrap}
.ed li small{grid-column:2/4;color:var(--cinza);font-size:12.5px;margin-top:2px}
.ed i{width:12px;height:12px;border-radius:50%;justify-self:center}
.ed-e{background:var(--verde)}
.ed-r{box-shadow:inset 0 0 0 3px var(--azul)}
.ed-c{border-radius:2px!important;transform:rotate(45deg);background:var(--navy);width:11px!important;height:11px!important}
.ed-m{background:var(--verde);box-shadow:0 0 0 3px rgba(16,173,49,.25)}
.eg{display:grid;gap:12px;padding:18px 20px 4px}
.eb h4,.et-th-cab h4,.fc h4{font:600 12.5px/1.2 var(--f-txt);letter-spacing:.11em;text-transform:uppercase;color:var(--verde-esc);margin:0 0 10px}
.eb{background:#F7F8F9;border-radius:0 20px 20px 20px;padding:16px 16px 14px}
.eb h4 span{display:inline-grid;place-items:center;min-width:22px;height:22px;padding:0 6px;border-radius:11px;background:var(--amarelo);color:var(--navy);margin-left:6px;letter-spacing:0;vertical-align:1px}
.eb-val{background:#FFF8DA}
.eb-prec{background:#EAF6FB}
.eo{list-style:none;margin:0;padding:0;display:grid;gap:8px}
.eo li{display:grid;grid-template-columns:22px 1fr;gap:10px;font-size:14.5px;line-height:1.45;color:var(--texto)}
.eo li::before{content:"";width:17px;height:17px;margin-top:3px;border-radius:0 6px 6px 6px;box-shadow:inset 0 0 0 2px var(--verde)}
.ev{list-style:none;margin:0;padding:0;display:grid;gap:10px}
.ev li{display:grid;grid-template-columns:auto 1fr;gap:10px;font-size:14px;line-height:1.45;color:#3a2d00}
.ev a{align-self:start;background:var(--navy);color:#fff;text-decoration:none;font-size:12px;font-weight:600;line-height:1;padding:6px 8px;border-radius:0 9px 9px 9px;white-space:nowrap;margin-top:1px}
.ev a:hover{background:var(--azul)}
.ev-vazio{margin:0;font-size:14.5px;color:#3a2d00}
.ep{list-style:none;margin:0;padding:0;display:grid;gap:10px}
.ep li{display:grid;gap:2px;font-size:14.5px;line-height:1.4}
.ep b{font-weight:600;color:var(--azul);font-size:13px}
@media (min-width:900px){
 .et-cab{grid-template-columns:auto 1fr;padding:30px 32px 22px;gap:26px}
 .et-num{width:112px;height:124px}.et-num b{font-size:58px}
 .et h3{font-size:34px}
 .et-num{grid-row:1/3}
 .et-tt{align-self:end}
 .ec{grid-column:2;max-width:640px;border-top:0;padding-top:0}
 .ed{grid-template-columns:repeat(3,1fr);padding:0 32px;gap:14px}
 .ed li{border-top:0;background:#F7F8F9;border-radius:0 16px 16px 16px;padding:12px 14px;grid-template-columns:18px 1fr;row-gap:2px}
 .ed li b{grid-column:2}
 .ed li small{grid-column:2}
 .eg{grid-template-columns:1fr 1fr;padding:18px 32px 4px;gap:14px}
 .eg3{grid-template-columns:1.05fr 1.15fr .8fr}
}

/* miniaturas */
.et-th{padding:20px 0 6px}
.et-th-cab{display:flex;align-items:baseline;justify-content:space-between;gap:12px;padding:0 20px}
.et-th-cab span{font-size:12.5px;color:var(--cinza)}
.ths{display:grid;grid-auto-flow:column;grid-auto-columns:62%;gap:12px;overflow-x:auto;scroll-snap-type:x mandatory;padding:4px 20px 14px;scroll-padding:0 20px;-webkit-overflow-scrolling:touch;overscroll-behavior-x:contain}
.th{scroll-snap-align:start;text-decoration:none;color:var(--navy);display:grid;gap:6px;align-content:start}
.th-i{display:block;border-radius:0 12px 12px 12px;overflow:hidden;box-shadow:0 0 0 1px var(--linha),0 12px 22px -16px rgba(7,32,71,.5);background:#E9ECEF;aspect-ratio:16/9;transition:transform .25s ease,box-shadow .25s ease}
.th-i img{width:100%;height:100%;object-fit:cover}
.th:hover .th-i{transform:translateY(-3px);box-shadow:0 0 0 2px var(--c),0 18px 28px -18px rgba(7,32,71,.6)}
.th-p{font:600 12px/1 var(--f-txt);color:var(--cinza)}
.th-t{font-size:13.5px;line-height:1.3;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
@media (min-width:640px){.ths{grid-auto-columns:40%}}
@media (min-width:900px){
 .et-th{padding:24px 32px 6px}.et-th-cab{padding:0}
 .ths{grid-auto-flow:row;grid-template-columns:repeat(4,1fr);grid-auto-columns:auto;overflow:visible;padding:4px 0 10px;gap:18px 16px}
}

/* ações */
.et-ac{display:flex;flex-wrap:wrap;gap:10px;padding:12px 20px 22px}
@media (min-width:900px){.et-ac{padding:14px 32px 28px}}
.btn{display:inline-flex;align-items:center;gap:10px;border:0;background:var(--verde);color:var(--navy);font:600 15.5px/1 var(--f-txt);padding:15px 22px;border-radius:0 24px 24px 24px;text-decoration:none;transition:background .2s,transform .2s}
.btn:hover{background:#13c238;transform:translateY(-1px)}
.btn-2{background:transparent;box-shadow:inset 0 0 0 2px var(--navy)}
.btn-2:hover{background:var(--navy);color:#fff}
@media (max-width:480px){.et-ac .btn{width:100%;justify-content:center}}

/* retorno */
.rt{margin:0 20px 22px;border-radius:0 22px 22px 22px;background:#F2F7FB;box-shadow:inset 0 0 0 1.5px #CFE3F1}
@media (min-width:900px){.rt{margin:0 32px 30px}}
.rt summary{list-style:none;cursor:pointer;padding:16px 18px;display:grid;grid-template-columns:1fr auto;align-items:center;gap:2px 12px}
.rt summary::-webkit-details-marker{display:none}
.rt summary span{font:400 20px/1.15 var(--f-tit)}
.rt summary small{grid-column:1;font-size:13px;color:var(--cinza)}
.rt summary::after{content:"+";grid-column:2;grid-row:1/3;width:34px;height:34px;border-radius:50%;background:var(--navy);color:#fff;display:grid;place-items:center;font:400 22px/1 var(--f-txt)}
.rt[open] summary::after{content:"−"}
.rt-in{padding:4px 18px 20px;display:grid;gap:18px}
.rt-l{display:block;font:600 12.5px/1.2 var(--f-txt);letter-spacing:.1em;text-transform:uppercase;color:var(--navy);margin:0 0 8px}
.rt-l small{text-transform:none;letter-spacing:0;font-weight:400;color:var(--cinza)}
.rt-sit{border:0;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:8px}
.rt-sit legend{padding:0}
.rt-sit label{position:relative}
.rt-sit input{position:absolute;opacity:0;inset:0;margin:0;cursor:pointer}
.rt-sit label span{display:inline-flex;align-items:center;gap:9px;padding:11px 16px 11px 12px;background:#fff;border-radius:0 18px 18px 18px;box-shadow:inset 0 0 0 1.5px var(--linha);font-size:14.5px;font-weight:500}
.rt-sit label span i{width:16px;height:16px;border-radius:50%;box-shadow:inset 0 0 0 2px #9AA6B5}
.rt-sit input:checked+span{background:var(--navy);color:#fff;box-shadow:none}
.rt-sit input:checked+span i{background:var(--verde);box-shadow:inset 0 0 0 3px #fff}
.rt-sit input:focus-visible+span{outline:3px solid var(--ciano);outline-offset:2px}
.rt-linha{display:grid;grid-template-columns:1fr auto;gap:8px;margin-bottom:10px;background:#fff;border-radius:0 16px 16px 16px;padding:10px;box-shadow:inset 0 0 0 1px var(--linha)}
.rt-linha select{grid-column:1;font:500 14px var(--f-txt);color:var(--navy);padding:9px 10px;border:1px solid var(--linha);border-radius:10px;background:#fff;max-width:100%;min-width:0}
.rt-linha textarea{grid-column:1/-1}
.rt-linha .rt-x{grid-column:2;grid-row:1;border:0;background:#EEF0F3;width:38px;border-radius:10px;font-size:18px;color:var(--cinza)}
textarea{width:100%;font:400 15px/1.45 var(--f-txt);color:var(--navy);border:1px solid var(--linha);border-radius:12px;padding:10px 12px;background:#fff;resize:vertical}
textarea:focus,select:focus{outline:2px solid var(--ciano);outline-offset:1px;border-color:transparent}
.rt-mais{border:0;background:none;color:var(--azul);font-weight:600;font-size:14.5px;padding:6px 0}
.rt-val{display:grid;gap:12px}
.rt-vi{display:grid;gap:6px}
.rt-vi span{font-size:13.5px;line-height:1.4;color:var(--texto)}
.rt-vi b{font-weight:600;color:var(--navy)}
.rt-prev textarea{background:#F7F8F9;font-size:13.5px;color:var(--texto)}
.rt-ac{display:flex;flex-wrap:wrap;align-items:center;gap:10px 16px}
.rt-ok{font-size:14px;color:var(--verde-esc);font-weight:600}
.rt-limpa{border:0;background:none;color:var(--cinza);font-size:13px;text-decoration:underline;text-underline-offset:3px;margin-left:auto;padding:6px 0}
.rt-obs{margin:0;font-size:12.5px;color:var(--cinza)}
@media (min-width:900px){.rt-in{padding:4px 22px 24px}.rt-linha{grid-template-columns:240px 1fr auto;align-items:start}.rt-linha textarea{grid-column:2}.rt-linha .rt-x{grid-column:3;height:38px}}

/* precisamos */
.pd{list-style:none;margin:0;padding:0;display:grid;gap:10px}
.pd li{display:grid;grid-template-columns:62px 1fr;gap:4px 14px;align-items:start;background:#fff;border-radius:0 20px 20px 20px;padding:14px 16px;box-shadow:0 1px 0 var(--linha)}
.pd time{grid-row:1/3;background:var(--navy);color:#fff;border-radius:0 14px 14px 14px;text-align:center;padding:8px 4px;line-height:1.1}
.pd time b{display:block;font:400 18px/1.1 var(--f-tit)}
.pd time span{font-size:11.5px;opacity:.75}
.pd-t{font-weight:500;font-size:15px;line-height:1.4}
.pd a{font-size:13px;color:var(--azul);text-decoration:none;font-weight:500}
.pd a:hover{text-decoration:underline}
@media (min-width:900px){.pd{grid-template-columns:1fr 1fr;gap:14px}}

/* reta final */
.final{background:var(--navy-2);color:#fff;margin-top:80px;position:relative;overflow:hidden}
.final-f{height:58vw;max-height:420px;position:relative;overflow:hidden}
.final-f img{width:100%;height:100%;object-fit:cover;object-position:72% 60%}
.final-f::after{content:"";position:absolute;inset:auto 0 0 0;height:45%;background:linear-gradient(to top,var(--navy-2),rgba(11,31,69,0))}
.final-t{position:relative;padding-top:8px;padding-bottom:56px}
.final .mao{color:var(--ciano)}
.final h2{font-size:34px;line-height:1.1;margin:6px 0 10px}
.final .lead{color:rgba(255,255,255,.8);max-width:40em;margin:0 0 26px}
.fcs{display:grid;gap:16px}
.fc{position:relative;background:#fff;color:var(--navy);border-radius:0 26px 26px 26px;padding:22px 20px 20px}
.fc-k{width:52px;height:52px;border-radius:0 18px 18px 18px;background:var(--c);color:var(--t);display:grid;place-items:center;font:400 26px/1 var(--f-tit);margin-bottom:12px}
.fc h3{font-size:26px;margin-bottom:6px}
.fc-d{margin:0 0 12px;color:var(--texto);font-size:15px}
.fc .ed{padding:0;margin-bottom:16px}
.fc-prec{margin-top:14px;background:#EAF6FB;border-radius:0 18px 18px 18px;padding:14px 16px}
.marcos{list-style:none;margin:22px 0 0;padding:0;display:grid;gap:10px}
.marcos li{display:grid;grid-template-columns:auto 1fr;gap:4px 14px;align-items:center;padding:14px 16px;border-radius:0 20px 20px 20px;background:rgba(255,255,255,.07);box-shadow:inset 0 0 0 1px rgba(255,255,255,.14)}
.marcos b{font:400 22px/1.1 var(--f-tit);color:var(--verde)}
.marcos span{font-size:15px;color:rgba(255,255,255,.88)}
@media (min-width:900px){
 .final{display:grid;grid-template-columns:1fr}
 .final-f{position:absolute;inset:0 0 auto 52%;height:520px;max-height:none}
 .final-f::after{inset:0 auto 0 0;width:50%;height:auto;background:linear-gradient(to right,var(--navy-2),rgba(11,31,69,0))}
 .final-t{padding-top:80px;padding-bottom:80px}
 .final-c{max-width:560px;min-height:360px}
 .final h2{font-size:48px}
 .fcs{grid-template-columns:1fr 1fr;gap:20px;margin-top:20px}
 .fc{padding:30px}
 .fc .ed li{font-size:13.5px}
 .marcos{grid-template-columns:repeat(3,1fr)}
}

/* rodapé */
.rodape{background:#06182f;color:rgba(255,255,255,.72);padding:36px 0 44px;font-size:13.5px}
.rodape .w{display:flex;flex-wrap:wrap;align-items:center;gap:16px 28px}
.rodape img{height:30px;width:auto}
.rodape p{margin:0;flex:1;min-width:220px;line-height:1.55}
.rodape a{color:#fff}

@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}.js .gb{transform:none}}
@media print{
 body{background:#fff}
 .topo,.final{background:#0B1F45!important;-webkit-print-color-adjust:exact;print-color-adjust:exact}
 .rt,.et-ac,.agora{display:none!important}
 .gantt{display:block!important;break-inside:avoid}.tl{display:none!important}.js .gb{transform:none!important}
 .et{break-inside:avoid-page;box-shadow:0 0 0 1px var(--linha)}
 .ths{grid-auto-flow:row!important;grid-template-columns:repeat(6,1fr)!important;overflow:visible!important}
}
"""

JS_CRONO = r"""
(function(){
  var d=document; d.documentElement.classList.add("js");
  var DADOS=JSON.parse(d.getElementById("dados").textContent);
  function $$(s,r){return Array.prototype.slice.call((r||d).querySelectorAll(s));}
  function guarda(k,v){try{if(v===undefined)return localStorage.getItem(k);localStorage.setItem(k,v);}catch(e){return null;}}
  function hojeISO(){var t=new Date();return t.getFullYear()+"-"+String(t.getMonth()+1).padStart(2,"0")+"-"+String(t.getDate()).padStart(2,"0");}
  var hoje=hojeISO();

  /* onde estamos */
  var ag=d.querySelector("[data-agora]");
  DADOS.janelas.forEach(function(j){ if(hoje>=j.de&&hoje<=j.ate){ ag.querySelector("span").textContent=j.txt; ag.hidden=false; } });
  $$(".et").forEach(function(c){ if(hoje>=c.getAttribute("data-envio")&&hoje<=c.getAttribute("data-check")){ var s=c.querySelector(".et-agora"); if(s) s.hidden=false; } });

  /* hoje na linha do tempo */
  var g=d.querySelector(".gantt");
  if(g){
    var ini=new Date(g.getAttribute("data-ini")+"T12:00:00"), dias=+g.getAttribute("data-dias"), agora=new Date(hoje+"T12:00:00");
    var x=(agora-ini)/864e5; var h=g.querySelector(".gh-hoje");
    if(x>=0&&x<dias){ h.style.left=((x+.5)/dias*100)+"%"; h.hidden=false; }
    if("IntersectionObserver" in window){ var ob=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){g.classList.add("viu");ob.disconnect();}});},{threshold:.25}); ob.observe(g); }
    else g.classList.add("viu");
  }
  var marcou=false;
  $$(".tl-i[data-d]").forEach(function(li){ var dd=li.getAttribute("data-d"); if(!marcou&&dd>=hoje){ li.classList.add("hoje"); li.querySelector("time").setAttribute("data-rot", dd===hoje?"hoje":"próximo"); marcou=true; } });

  /* retorno por etapa */
  var CH="ourofino-cronograma-retorno-v1", est={};
  try{ est=JSON.parse(guarda(CH)||"{}")||{}; }catch(e){ est={}; }
  function salva(){ guarda(CH,JSON.stringify(est)); }

  $$(".rt").forEach(function(rt){
    var n=rt.getAttribute("data-etapa"), E=DADOS.etapas[n-1];
    var st=est[n]||(est[n]={sit:"",linhas:[],val:{},geral:""});
    var caixa=rt.querySelector("[data-linhas]"), previa=rt.querySelector("[data-previa]"), ok=rt.querySelector("[data-ok]");
    function opcoes(sel){ return E.paginas.map(function(p){ return '<option value="'+p.pg+'"'+(String(p.pg)===String(sel)?" selected":"")+'>p. '+p.pg+' · '+p.titulo.replace(/</g,"&lt;")+'</option>'; }).join(""); }
    function linha(l,i){
      var div=d.createElement("div"); div.className="rt-linha";
      div.innerHTML='<select aria-label="Página"><option value="">Escolha a página</option>'+opcoes(l.pg)+'</select>'+
        '<button type="button" class="rt-x" aria-label="Tirar este ajuste">×</button>'+
        '<textarea rows="2" placeholder="O que ajustar nesta página"></textarea>';
      var sel=div.querySelector("select"), ta=div.querySelector("textarea");
      ta.value=l.txt||"";
      sel.addEventListener("change",function(){ l.pg=sel.value; muda(); });
      ta.addEventListener("input",function(){ l.txt=ta.value; muda(); });
      div.querySelector(".rt-x").addEventListener("click",function(){ st.linhas.splice(st.linhas.indexOf(l),1); if(!st.linhas.length) st.linhas.push({pg:"",txt:""}); desenha(); muda(); });
      return div;
    }
    function desenha(){ caixa.innerHTML=""; if(!st.linhas.length) st.linhas.push({pg:"",txt:""}); st.linhas.forEach(function(l,i){ caixa.appendChild(linha(l,i)); }); }
    function texto(){
      var L=[], tit=function(pg){ var p=E.paginas.filter(function(x){return String(x.pg)===String(pg);})[0]; return p?p.titulo:""; };
      L.push("Guia de Execução no PDV · Ourofino Pet");
      L.push("Retorno da etapa "+n+" de "+DADOS.total+": "+E.nome+" (páginas "+E.de+" a "+E.ate+")");
      L.push("");
      L.push("Situação: "+(st.sit||"(marque Aprovada, Aprovada com ajustes ou Refazer)"));
      var aj=st.linhas.filter(function(l){return (l.txt||"").trim();}).slice().sort(function(a,b){return (+a.pg||999)-(+b.pg||999);});
      if(aj.length){ L.push(""); L.push("Ajustes por página"); aj.forEach(function(l){ L.push("• "+(l.pg?"p. "+l.pg+" ("+tit(l.pg)+")":"Página não indicada")+": "+l.txt.trim()); }); }
      var vs=E.notas.map(function(v,i){ return [v,(st.val[i]||"").trim()]; }).filter(function(x){return x[1];});
      if(vs.length){ L.push(""); L.push("Pontos para validar"); vs.forEach(function(x){ L.push("• p. "+x[0].pg+" ("+x[0].curto+"): "+x[1]); }); }
      if((st.geral||"").trim()){ L.push(""); L.push("Comentário geral"); L.push(st.geral.trim()); }
      return L.join("\n");
    }
    function muda(){ previa.value=texto(); ok.textContent=""; salva(); }
    $$('input[type="radio"]',rt).forEach(function(r){ r.checked=(r.value===st.sit); r.addEventListener("change",function(){ st.sit=r.value; muda(); }); });
    $$("[data-val]",rt).forEach(function(t){ var i=t.getAttribute("data-val"); t.value=st.val[i]||""; t.addEventListener("input",function(){ st.val[i]=t.value; muda(); }); });
    var ge=rt.querySelector("[data-geral]"); ge.value=st.geral||""; ge.addEventListener("input",function(){ st.geral=ge.value; muda(); });
    rt.querySelector("[data-mais]").addEventListener("click",function(){ var l={pg:"",txt:""}; st.linhas.push(l); caixa.appendChild(linha(l)); caixa.lastChild.querySelector("select").focus(); salva(); });
    rt.querySelector("[data-limpa]").addEventListener("click",function(){
      if(!confirm("Apagar o rascunho do retorno desta etapa?")) return;
      st=est[n]={sit:"",linhas:[],val:{},geral:""}; $$('input[type="radio"]',rt).forEach(function(r){r.checked=false;});
      $$("[data-val]",rt).forEach(function(t){t.value="";}); ge.value=""; desenha(); muda();
    });
    rt.querySelector("[data-copia]").addEventListener("click",function(){
      var t=texto(); previa.value=t;
      function feito(){ ok.textContent="Copiado. Agora é só colar no e-mail ou no WhatsApp."; }
      function velho(){ previa.removeAttribute("readonly"); previa.focus(); previa.select(); var c=false; try{ c=d.execCommand("copy"); }catch(e){} previa.setAttribute("readonly",""); if(c) feito(); else ok.textContent="Selecione o texto acima e copie."; }
      if(navigator.clipboard&&window.isSecureContext){ navigator.clipboard.writeText(t).then(feito,velho); } else velho();
    });
    desenha(); previa.value=texto();
  });

  $$("[data-abre-rt]").forEach(function(b){ b.addEventListener("click",function(){ var rt=d.getElementById("retorno-"+b.getAttribute("data-abre-rt")); rt.open=true; rt.scrollIntoView({behavior:"smooth",block:"start"}); }); });
  function doHash(){ var h=location.hash.slice(1); var m=/^retorno-(\d+)$/.exec(h); if(m){ var rt=d.getElementById(h); if(rt){ rt.open=true; setTimeout(function(){ rt.scrollIntoView({block:"start"}); },60); } } }
  addEventListener("hashchange",doHash); doHash();
})();
"""


def cronograma(guia):
    n_tot = len(ETAPAS)
    total = len(guia["slides"])
    a, b = FINAIS
    dados = dict(total=n_tot, janelas=janelas(), etapas=[
        dict(n=e["n"], nome=e["nome"], de=e["de"], ate=e["ate"],
             paginas=[dict(pg=s["pg"], titulo=s["titulo"]) for s in e["slides"]],
             notas=[dict(pg=x["pg"], curto=(x["texto"][:70].rsplit(" ", 1)[0] + "…") if len(x["texto"]) > 70 else x["texto"]) for x in e["notas"]])
        for e in ETAPAS])
    ver = re.sub(r"\s*·\s*em validação.*$", "", guia["versao"])
    ver = ("Guia na " + ver[0].lower() + ver[1:]) if ver else "Guia em validação"
    dados_js = json.dumps(dados, ensure_ascii=False).replace("</", "<\\/")
    geo = GEO.format(geo_paths())
    logo75 = '<img src="75lab-logo-branco.svg" alt="75 LAB" width="42" height="30">' if os.path.exists(os.path.join(R, "cronograma", "75lab-logo-branco.svg")) else "<b>75 LAB</b>"
    etapas_html = "".join(card_etapa(e, n_tot) for e in ETAPAS)
    nnotas = sum(len(e["notas"]) for e in ETAPAS)
    doc = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Cronograma de aprovação · Guia de Execução no PDV · Ourofino Pet</title>
<meta name="description" content="Cronograma de aprovação do Guia de Execução no PDV da Ourofino Pet, etapa por etapa.">
<meta name="robots" content="noindex">
<meta name="theme-color" content="#0B1F45">
<link rel="icon" href="../assets/marca/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Young+Serif&family=Poppins:wght@400;500;600;700&family=Caveat:wght@600;700&display=swap" rel="stylesheet">
<style>{CSS_CRONO}</style>
</head>
<body>
<header class="topo">
  <figure class="topo-f" style="margin:0"><img src="../assets/img/v6/v6-capa.webp" srcset="../assets/img/v6/v6-capa-900.webp 900w, ../assets/img/v6/v6-capa.webp 1800w" sizes="(min-width:900px) 62vw, 100vw" width="1800" height="1200" alt="Golden retriever e gato branco, a capa do guia"></figure>
  <div class="topo-geo" aria-hidden="true">{geo}</div>
  <div class="topo-t w"><div class="topo-c">
    <div class="topo-marcas"><img src="../assets/marca/logo-negativo.svg" alt="Ourofino Saúde Animal" width="150" height="26"><span>Guia de Execução no PDV<br>Ourofino Pet</span></div>
    <span class="mao">cronograma de aprovação</span>
    <h1>O guia, etapa por etapa</h1>
    <p class="lead">O guia tem <b>{total} páginas</b>. Para a Ourofino revisar com calma, dividimos o material em <b>{n_tot} etapas</b>. Toda quinta, no touchpoint, damos o check em uma etapa e mandamos a próxima.</p>
    <p class="agora" data-agora hidden><i></i><span></span></p>
    <ul class="fatos">
      <li><span>Entrega</span><b>{dsem(ENTREGA)}/{D(ENTREGA).year}</b><small>prazo combinado na reunião de 19/11</small></li>
      <li><span>Convenção</span><b>1ª semana de março</b><small>guia pronto, impresso e digital</small></li>
      <li><span>Aprovação</span><b>bloco a bloco</b><small>com check no touchpoint semanal</small></li>
    </ul>
  </div></div>
</header>

<main>
<section class="sec w" id="como">
  <div class="sec-cab"><span class="mao">como funciona</span><h2>Uma etapa por semana</h2></div>
  <ol class="passos">
    <li><span>1</span><div><small>quinta</small><b>A 75 LAB envia a etapa</b><p>Você recebe o link só com as páginas daquela etapa, na mesma numeração do guia completo.</p></div></li>
    <li><span>2</span><div><small>até a quarta seguinte</small><b>A Ourofino responde</b><p>Marque Aprovada, Aprovada com ajustes ou Refazer, anote os ajustes por página e copie o retorno para o e-mail ou o WhatsApp.</p></div></li>
    <li><span>3</span><div><small>quinta, no touchpoint</small><b>Check e próxima etapa</b><p>Fechamos os ajustes juntos, a etapa ganha o check e a próxima já sai no mesmo dia.</p></div></li>
  </ol>
</section>

<section class="sec w" id="linha-do-tempo">
  <div class="sec-cab"><span class="mao">linha do tempo</span><h2>De hoje até a convenção</h2>
    <p>Na semana de Natal e Ano-Novo não há envios. A etapa 4 tem prazo maior porque passa pelo regulatório e pelo fim de ano.</p></div>
  {gantt()}
  <div class="g-leg"><span><i class="lg-e"></i>envio da 75 LAB</span><span><i class="lg-b"></i>com a Ourofino para revisar</span><span><i class="lg-c"></i>check no touchpoint</span><span><i class="lg-p"></i>pausa</span></div>
  {eventos()}
</section>

<section class="sec w" id="etapas">
  <div class="sec-cab"><span class="mao">as {n_tot} etapas</span><h2>O que entra em cada etapa</h2>
    <p>Cada etapa tem o seu link para aprovar, as páginas que entram, o que vale conferir e os {nnotas} pontos que dependem de uma confirmação da Ourofino.</p></div>
  <div class="ets">{etapas_html}</div>
</section>

<section class="sec w" id="precisamos">
  <div class="sec-cab"><span class="mao">o que precisamos de vocês</span><h2>Materiais da Ourofino e até quando</h2>
    <p>Com estes materiais em mãos, trocamos o que hoje é provisório no guia pela versão oficial da Ourofino.</p></div>
  <ul class="pd">{pedidos()}</ul>
</section>
</main>

<section class="final" id="reta-final">
  <figure class="final-f" style="margin:0"><img src="../assets/img/v6/v6-fim.webp" srcset="../assets/img/v6/v6-fim-900.webp 900w, ../assets/img/v6/v6-fim.webp 1800w" sizes="(min-width:900px) 48vw, 100vw" width="1800" height="1200" alt="Filhotes de cão e gato dormindo juntos" loading="lazy"></figure>
  <div class="final-t w">
    <div class="final-c"><span class="mao">reta final</span><h2>Depois das {n_tot} etapas</h2>
    <p class="lead">Juntamos tudo num guia só, conferimos com vocês e fechamos a arte final para impressão e para o link digital.</p></div>
    <div class="fcs">{card_final(a)}{card_final(b)}</div>
    <ul class="marcos">
      <li><b>{dm(b["retorno"])}</b><span>aprovação final da arte</span></li>
      <li><b>{dm(ENTREGA)}</b><span>entrega oficial do guia</span></li>
      <li><b>março</b><span>1ª semana: guia pronto para a convenção</span></li>
    </ul>
  </div>
</section>

<footer class="rodape"><div class="w">{logo75}<p>Cronograma feito pela 75 LAB para a Ourofino Pet. {esc(ver)}. Atualizado em {dm(HOJE)}/{HOJE.year}.</p><a href="../">Abrir o guia completo</a></div></footer>
<script type="application/json" id="dados">{dados_js}</script>
<script>{JS_CRONO}</script>
</body>
</html>
"""
    os.makedirs(os.path.join(R, "cronograma"), exist_ok=True)
    with open(os.path.join(R, "cronograma", "index.html"), "w", encoding="utf-8") as f:
        f.write(doc)


# ---------------------------------------------------------------- principal
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sem-miniaturas", action="store_true", help="não refaz as miniaturas")
    ap.add_argument("--perfil", help="pasta de perfil do Chrome headless")
    a = ap.parse_args()
    TIT_MD.update(titulos_md())
    guia = le_guia()
    print(f"guia: {len(guia['slides'])} slides · {guia['versao']}")
    monta_etapas(guia)
    for e in ETAPAS: pacote(e, guia, len(ETAPAS))
    print(f"  {len(ETAPAS)} pacotes em aprovacao/etapa-N/")
    if not a.sem_miniaturas: miniaturas(len(guia["slides"]), a.perfil)
    falta = [s["pg"] for s in guia["slides"] if not os.path.exists(os.path.join(R, "aprovacao", "miniaturas", nome_mini(s["pg"])))]
    if falta: print("  aviso: sem miniatura para as páginas", falta)
    cronograma(guia)
    print("  cronograma/index.html")


if __name__ == "__main__":
    main()
