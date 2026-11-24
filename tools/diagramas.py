"""Diagramas desenhados à mão (SVG/HTML) para o guia. Cada função retorna HTML pronto."""

NAVY = "#072047"; VERDE = "#10AD31"; AZUL = "#007CC1"; CINZA = "#8A94A3"; LINHA = "#C9CED6"; PAPEL = "#FFFFFF"

def ic(nome, s=44):
    """ícones de traço, mesmo peso de linha (1.8) e cantos arredondados"""
    p = {
        "fabrica": '<path d="M4 40V20l10 6v-6l10 6v-6l10 6V8h6v32z"/><path d="M4 40h36"/><path d="M12 32h4M20 32h4M28 32h4"/>',
        "caminhao": '<path d="M3 30V12h22v18"/><path d="M25 18h8l6 7v5h-3"/><circle cx="11" cy="32" r="3.5"/><circle cx="32" cy="32" r="3.5"/><path d="M14.5 32h14"/>',
        "loja": '<path d="M5 18l3-9h28l3 9"/><path d="M5 18c0 3 2.5 4.5 5.5 4.5S16 21 16 18c0 3 2.5 4.5 5.5 4.5S27 21 27 18c0 3 2.5 4.5 5.5 4.5S38 21 38 18"/><path d="M8 22v17h28V22"/><path d="M18 39V29h8v10"/>',
        "tutor": '<circle cx="15" cy="9" r="4.5"/><path d="M7 39V24a8 8 0 0 1 16 0v15"/><path d="M23 30l6-2c3 0 5 1 7 3l3-1v4l-3 2v3h-3v-3h-6v3h-3"/><path d="M36 28l1-4 2 2"/>',
        "pata": '<ellipse cx="22" cy="29" rx="8" ry="7"/><circle cx="12" cy="19" r="3.5"/><circle cx="18" cy="13" r="3.5"/><circle cx="26" cy="13" r="3.5"/><circle cx="32" cy="19" r="3.5"/>',
        "cruz": '<path d="M17 6h10v11h11v10H27v11H17V27H6V17h11z"/>',
        "relogio": '<circle cx="22" cy="22" r="16"/><path d="M22 12v10l7 5"/>',
    }[nome]
    return (f'<svg class="ic" viewBox="0 0 44 44" width="{s}" height="{s}" fill="none" stroke="currentColor" '
            f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{p}</svg>')

def caminho_produto():
    etapas = [("fabrica", "Ourofino", "fabrica o produto"), ("caminhao", "Distribuidor", "compra, estoca e entrega"),
              ("loja", "Loja", "expõe, orienta e vende"), ("tutor", "Tutor", "leva para casa e usa no pet")]
    setas = ["abastecimento", "sell-in", "sell-out"]
    h = ['<div class="dg dg-caminho" role="img" aria-label="Caminho do produto da Ourofino até o tutor">']
    for i, (icn, t, s) in enumerate(etapas):
        h.append(f'<div class="cam-no"><span class="cam-ic">{ic(icn, 46)}</span><b>{t}</b><small>{s}</small></div>')
        if i < 3:
            cls = "seta destaque" if setas[i] != "abastecimento" else "seta"
            h.append(f'<div class="cam-seta {cls}"><span>{setas[i]}</span></div>')
    h.append('</div>')
    return "".join(h)

def visita():
    col = [
        ("Antes", "fora da loja", ["Defina o objetivo da visita", "Separe material e kit", "Revise as pendências da última visita", "Confira a rota e os horários"]),
        ("Durante", "dentro da loja, sempre nesta ordem", ["Chegue e se apresente", "Leia a loja", "Fotografe antes", "Corrija o básico", "Execute a prioridade do dia", "Converse com a equipe", "Fotografe depois", "Encerre com o responsável"]),
        ("Depois", "no mesmo dia", ["Registre a visita com as fotos", "Avise o supervisor sobre pendências", "Anote o que levar na próxima vez"]),
    ]
    h = ['<div class="dg dg-visita">']
    for i, (t, sub, itens) in enumerate(col):
        lis = "".join(f'<li><span>{k + 1:02d}</span>{x}</li>' for k, x in enumerate(itens))
        h.append(f'<div class="vis-col vis-{i}"><div class="vis-cab"><b>{t}</b><small>{sub}</small></div><ol>{lis}</ol></div>')
    h.append('</div>')
    return "".join(h)

def fifo():
    caixas = [("03/2027", "vence primeiro", VERDE), ("05/2027", "", "#5BC06E"), ("08/2027", "", "#9AD7A6"), ("11/2027", "lote novo", "#D3EDD8")]
    w, hh = 760, 300
    s = [f'<svg class="dg-svg" viewBox="0 0 {w} {hh}" role="img" aria-label="FIFO: produto que vence antes fica na frente">']
    s.append(f'<rect x="60" y="196" width="640" height="10" rx="2" fill="{NAVY}"/>')
    s.append(f'<rect x="60" y="206" width="640" height="26" fill="#EEF0F3" stroke="{LINHA}"/>')
    s.append(f'<text x="64" y="224" font-size="12" fill="{CINZA}" font-family="IBM Plex Mono, monospace">FRENTE · corredor</text>')
    s.append(f'<text x="696" y="224" font-size="12" fill="{CINZA}" text-anchor="end" font-family="IBM Plex Mono, monospace">FUNDO</text>')
    for i, (d, lab, c) in enumerate(caixas):
        x = 80 + i * 150
        s.append(f'<rect x="{x}" y="86" width="118" height="110" rx="6" fill="{c}" stroke="{NAVY}" stroke-width="1.6"/>')
        s.append(f'<rect x="{x + 16}" y="120" width="86" height="34" rx="4" fill="#fff" stroke="{NAVY}" stroke-width="1.2"/>')
        s.append(f'<text x="{x + 59}" y="134" font-size="10" text-anchor="middle" fill="{CINZA}" font-family="IBM Plex Mono, monospace">VALIDADE</text>')
        s.append(f'<text x="{x + 59}" y="149" font-size="14" font-weight="600" text-anchor="middle" fill="{NAVY}" font-family="Figtree, sans-serif">{d}</text>')
        if lab: s.append(f'<text x="{x + 59}" y="74" font-size="14" font-weight="700" text-anchor="middle" fill="{VERDE if i == 0 else NAVY}" font-family="Figtree, sans-serif">{lab}</text>')
    s.append(f'<path d="M748 140 h-40" stroke="{NAVY}" stroke-width="2" marker-end="url(#ponta)"/>')
    s.append(f'<path d="M66 140 h-40" stroke="{VERDE}" stroke-width="2.4" marker-end="url(#pontav)"/>')
    s.append(f'<text x="20" y="270" font-size="15" fill="{VERDE}" font-weight="700" font-family="Figtree, sans-serif">← o tutor pega da frente</text>')
    s.append(f'<text x="740" y="270" font-size="15" fill="{NAVY}" font-weight="700" text-anchor="end" font-family="Figtree, sans-serif">a reposição entra por trás ←</text>')
    s.append(f'<defs><marker id="ponta" markerWidth="10" markerHeight="10" refX="6" refY="5" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="{NAVY}"/></marker>'
             f'<marker id="pontav" markerWidth="10" markerHeight="10" refX="6" refY="5" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="{VERDE}"/></marker></defs>')
    s.append('</svg>')
    return '<div class="dg dg-fifo">' + "".join(s) + '</div>'

def blocagem():
    cores = [VERDE, AZUL, "#F2A33A", "#9B6BC9"]
    def gondola(x0, vertical, titulo):
        out = [f'<text x="{x0 + 150}" y="26" font-size="16" font-weight="700" text-anchor="middle" fill="{NAVY}" font-family="Figtree, sans-serif">{titulo}</text>']
        out.append(f'<rect x="{x0}" y="40" width="300" height="250" rx="4" fill="#F6F7F8" stroke="{NAVY}" stroke-width="1.6"/>')
        for r in range(4):
            y = 52 + r * 60
            out.append(f'<rect x="{x0}" y="{y + 50}" width="300" height="5" fill="{NAVY}"/>')
            for c in range(8):
                col = cores[c // 2] if vertical else cores[r]
                out.append(f'<rect x="{x0 + 8 + c * 36}" y="{y + 6}" width="31" height="44" rx="3" fill="{col}" opacity="0.92"/>')
        return "".join(out)
    s = ['<svg class="dg-svg" viewBox="0 0 700 330" role="img" aria-label="Blocagem vertical e horizontal">']
    s.append(gondola(20, True, "Blocagem vertical")); s.append(gondola(380, False, "Blocagem horizontal"))
    s.append(f'<text x="170" y="318" font-size="13" text-anchor="middle" fill="{CINZA}" font-family="Figtree, sans-serif">cada linha ocupa uma coluna</text>')
    s.append(f'<text x="530" y="318" font-size="13" text-anchor="middle" fill="{CINZA}" font-family="Figtree, sans-serif">cada linha ocupa uma prateleira</text>')
    s.append('</svg>')
    return '<div class="dg dg-bloc">' + "".join(s) + '</div>'

def cbv():
    d = [("C", "Característica", "O que o produto é ou tem.", "Comprimido palatável."),
         ("B", "Benefício", "O que isso faz pelo pet e pelo tutor.", "O cão aceita sem briga, e o tutor dá em casa sem estresse."),
         ("V", "Vantagem", "Por que escolher este.", "Até 45 dias de proteção com um comprimido.")]
    h = ['<div class="dg dg-cbv">']
    for i, (l, t, s, ex) in enumerate(d):
        h.append(f'<div class="cbv-degrau d{i}"><span class="cbv-l">{l}</span><b>{t}</b><p>{s}</p><em>Ex.: {ex}</em></div>')
    h.append('<p class="cbv-nota">Exemplo com WellPET, apenas ilustrativo. O argumento oficial de cada produto está no capítulo 11.</p></div>')
    return "".join(h)

def quem_decide():
    tipos = [("Petshop", ["pata"], "a venda é o centro"), ("Petshop com clínica", ["pata", "cruz"], "a loja é o centro, com consultório"),
             ("Clínica com petshop", ["cruz", "pata"], "o atendimento é o centro")]
    h = ['<div class="dg dg-tipos">']
    for t, icons, s in tipos:
        ics = "".join(ic(x, 34 if k else 46) for k, x in enumerate(icons))
        h.append(f'<div class="tipo"><span class="tipo-ic">{ics}</span><b>{t}</b><small>{s}</small></div>')
    h.append('</div>')
    return "".join(h)

def rota(pts, r=12):
    """caminho ortogonal com cantos arredondados"""
    d = f"M{pts[0][0]} {pts[0][1]}"
    for i in range(1, len(pts) - 1):
        (x0, y0), (x1, y1), (x2, y2) = pts[i - 1], pts[i], pts[i + 1]
        dx0, dy0 = (x1 - x0), (y1 - y0); l0 = max(abs(dx0), abs(dy0)) or 1
        dx1, dy1 = (x2 - x1), (y2 - y1); l1 = max(abs(dx1), abs(dy1)) or 1
        rr = min(r, l0 / 2, l1 / 2)
        a = (x1 - dx0 / l0 * rr, y1 - dy0 / l0 * rr); b = (x1 + dx1 / l1 * rr, y1 + dy1 / l1 * rr)
        d += f" L{a[0]:.1f} {a[1]:.1f} Q{x1} {y1} {b[0]:.1f} {b[1]:.1f}"
    d += f" L{pts[-1][0]} {pts[-1][1]}"
    return d

# ----------------------------------------------------------------- planta da loja
AREAS = {
    "entrada": (30, 470, 150, 70, "Entrada"),
    "vitrine": (190, 500, 250, 40, "Vitrine"),
    "caixa": (520, 380, 210, 70, "Caixa e balcão"),
    "farmacia": (520, 300, 210, 62, "Farmácia"),
    "racao_cao": (30, 60, 130, 230, "Ração de cão"),
    "racao_gato": (190, 60, 110, 150, "Ração de gato"),
    "acessorios": (190, 240, 160, 70, "Acessórios"),
    "higiene_pet": (330, 60, 130, 80, "Higiene e beleza"),
    "higiene_amb": (330, 160, 150, 60, "Higiene do ambiente"),
    "banho": (760, 60, 170, 170, "Banho e tosa"),
    "consultorio": (760, 260, 170, 130, "Consultório"),
    "espera": (760, 420, 170, 110, "Espera"),
}
def planta(setas=False):
    W, H = 960, 560
    s = [f'<svg class="dg-svg planta" viewBox="0 0 {W} {H}" role="img" aria-label="Planta de um petshop">']
    s.append(f'<rect x="10" y="40" width="{W - 20}" height="{H - 50}" fill="#FBFBFA" stroke="{NAVY}" stroke-width="5"/>')
    s.append(f'<rect x="40" y="{H - 14}" width="120" height="10" fill="#FBFBFA"/>')  # porta
    s.append(f'<path d="M40 {H - 10} q60 -70 120 0" fill="none" stroke="{CINZA}" stroke-dasharray="4 4"/>')
    s.append(f'<line x1="740" y1="40" x2="740" y2="{H - 10}" stroke="{NAVY}" stroke-width="3"/>')
    s.append(f'<line x1="740" y1="240" x2="{W - 10}" y2="240" stroke="{NAVY}" stroke-width="3"/>')
    s.append(f'<line x1="740" y1="405" x2="{W - 10}" y2="405" stroke="{NAVY}" stroke-width="3"/>')
    cores = {"farmacia": "#DCEFE0", "caixa": "#E6EEF7", "racao_cao": "#FBE7DA", "racao_gato": "#FDF0D5", "acessorios": "#EEE6F6",
             "higiene_pet": "#E3F4F8", "higiene_amb": "#DFF1F4", "banho": "#F2F3F5", "consultorio": "#F2F3F5", "espera": "#F2F3F5",
             "entrada": "#FFFFFF", "vitrine": "#FFFFFF"}
    for k, (x, y, w, h, nome) in AREAS.items():
        dash = ' stroke-dasharray="5 4"' if k in ("entrada", "vitrine") else ""
        s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{cores[k]}" stroke="{NAVY}" stroke-width="1.4"{dash}/>')
        s.append(f'<text x="{x + w / 2}" y="{y + h / 2 + 5}" font-size="15" font-weight="600" text-anchor="middle" fill="{NAVY}" font-family="Figtree, sans-serif">{nome}</text>')
    s.append(f'<text x="625" y="292" font-size="11" text-anchor="middle" fill="{VERDE}" font-weight="700" font-family="IBM Plex Mono, monospace">ATRÁS DO BALCÃO</text>')
    if setas:
        s.append(f'<defs><marker id="sm" markerUnits="userSpaceOnUse" markerWidth="12" markerHeight="12" refX="9" refY="6" orient="auto"><path d="M0 0 L12 6 L0 12 z" fill="{VERDE}"/></marker>'
                 f'<marker id="ss" markerUnits="userSpaceOnUse" markerWidth="12" markerHeight="12" refX="9" refY="6" orient="auto"><path d="M0 0 L12 6 L0 12 z" fill="{AZUL}"/></marker></defs>')
        rotas = [("1", [(150, 282), (150, 446), (497, 446), (497, 334), (516, 334)], VERDE, "sm", ""),
                 ("2", [(342, 314), (342, 424), (482, 424), (482, 348), (516, 348)], VERDE, "sm", ""),
                 ("3", [(296, 214), (296, 232), (505, 232), (505, 316), (516, 316)], VERDE, "sm", ""),
                 ("4", [(484, 196), (700, 196), (700, 296)], AZUL, "ss", ' stroke-dasharray="7 6"')]
        for num, pts, cor, mk, dash in rotas:
            s.append(f'<path d="{rota(pts)}" fill="none" stroke="{cor}" stroke-width="2.6" stroke-linejoin="round"{dash} marker-end="url(#{mk})"/>')
            x, y = pts[0]
            s.append(f'<circle cx="{x}" cy="{y}" r="13" fill="{cor}" stroke="#fff" stroke-width="2.5"/>'
                     f'<text x="{x}" y="{y + 4.5}" font-size="13" font-weight="700" fill="#fff" text-anchor="middle" font-family="Figtree, sans-serif">{num}</text>')
        s.append(f'<circle cx="478" cy="152" r="13" fill="{AZUL}" stroke="#fff" stroke-width="2.5"/>'
                 f'<text x="478" y="156.5" font-size="13" font-weight="700" fill="#fff" text-anchor="middle" font-family="Figtree, sans-serif">5</text>')
    s.append('</svg>')
    leg = ""
    if setas:
        itens = [("1", "sm", "Ração de cão", "material de WellPET e de Plenipil (para pele sensível)"),
                 ("2", "sm", "Coleiras e guias", "material de WellPET"),
                 ("3", "sm", "Ração de gato", "material de Banni 3"),
                 ("4", "ss", "Top Dog + Herbalvet T.A.", "vermífugo para o cão e desinfetante para o ambiente onde ele vive"),
                 ("5", "ss", "EnziClim + Herbalvet T.A.", "os dois cuidam do ambiente, lado a lado na gôndola")]
        li = "".join(f'<li><span class="n {c}">{n}</span><b>{t}</b> {d}</li>' for n, c, t, d in itens)
        leg = ('<div class="dg-leg"><div><span class="leg-t"><i class="l-sm"></i>Cross merchandising</span><small>o material fica na área e leva o tutor até a farmácia</small></div>'
               '<div><span class="leg-t"><i class="l-ss"></i>Cross selling</span><small>produtos que combinam, oferecidos juntos</small></div>'
               f'<ol class="leg-lista">{li}</ol></div>')
    return ('<div class="dg dg-planta"><div class="dg-rolagem">' + "".join(s) + '</div><p class="dg-dica-rol">Arraste para o lado para ver a planta inteira.</p>' + leg + '</div>')

DIAGRAMAS = {
    "D-CAMINHO-PRODUTO": caminho_produto, "D-VISITA": visita, "D-FIFO": fifo, "D-BLOCAGEM": blocagem,
    "D-CBV": cbv, "D-QUEM-DECIDE": quem_decide, "D-MAPA-LOJA": lambda: planta(False), "D-CROSS-MAPA": lambda: planta(True),
}

def mascote(s=64):
    """avatar provisório da Dica (substituir pela arte da turma do bite)"""
    return (f'<svg viewBox="0 0 64 64" width="{s}" height="{s}" aria-hidden="true"><circle cx="32" cy="32" r="31" fill="{VERDE}"/>'
            f'<g fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">'
            f'<path d="M17 26c0-6 3-11 7-12l3 9"/><path d="M47 26c0-6-3-11-7-12l-3 9"/>'
            f'<path d="M20 28c0 9 5 16 12 16s12-7 12-16c0-6-5-9-12-9s-12 3-12 9z"/>'
            f'<circle cx="26.5" cy="29" r="1.4" fill="#fff"/><circle cx="37.5" cy="29" r="1.4" fill="#fff"/>'
            f'<path d="M29.5 35.5h5l-2.5 2.5z" fill="#fff"/><path d="M32 38v2.5c0 1.6-1.6 2.6-3.2 2"/><path d="M32 40.5c0 1.6 1.6 2.6 3.2 2"/></g></svg>')
