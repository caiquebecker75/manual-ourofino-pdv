"""Ícones animados do guia (SVG 48x48, traço contínuo + um acento na cor da marca).
Cada traço se desenha quando o slide entra (classe .viu); partes com classe de movimento têm animação contínua sutil:
  m-gira (gira em torno do centro do ícone), m-balanca (pêndulo), m-pulsa, m-sobe, m-pisca, m-varre."""

# (traços, acentos) — traços: path/line/circle desenhados; acentos: formas preenchidas ou destacadas
I = {
    "loja": ('<path d="M7 20v20h34V20"/><path d="M5 12l3-6h32l3 6"/><path d="M5 12c0 4 3 6 6.3 6S17.6 16 17.6 12c0 4 3 6 6.4 6s6.4-2 6.4-6c0 4 3 6 6.3 6S43 16 43 12"/><path d="M20 40V29h8v11"/>',
             '<path class="ac m-pulsa" d="M31 26h6v6h-6z"/>'),
    "caminhao": ('<path d="M4 31V13h24v18"/><path d="M28 19h8l7 8v4h-3"/><path d="M15 33h14"/>',
                 '<circle class="ac m-gira" cx="11" cy="33" r="3.6"/><circle class="ac m-gira" cx="35" cy="33" r="3.6"/>'),
    "fabrica": ('<path d="M5 41V22l10 6v-6l10 6v-6l10 6V9h7v32z"/><path d="M5 41h38"/>',
                '<path class="ac m-sobe" d="M36 6c0-2 2-3 3-2"/><path class="ac" d="M13 34h4M21 34h4M29 34h4"/>'),
    "pata": ('<path d="M24 40c-6 0-10-3-10-7 0-5 5-9 10-9s10 4 10 9c0 4-4 7-10 7z"/>',
             '<circle class="ac m-pulsa" cx="13" cy="20" r="3.4"/><circle class="ac m-pulsa" cx="19.5" cy="13" r="3.4"/><circle class="ac m-pulsa" cx="28.5" cy="13" r="3.4"/><circle class="ac m-pulsa" cx="35" cy="20" r="3.4"/>'),
    "vet": ('<circle cx="24" cy="24" r="17"/>', '<path class="ac m-pulsa" d="M20 14h8v6h6v8h-6v6h-8v-6h-6v-8h6z"/>'),
    "relogio": ('<circle cx="24" cy="24" r="17"/><path d="M24 9v3M24 36v3M9 24h3M36 24h3"/>',
                '<path class="ac m-gira" d="M24 24V15"/><path class="ac" d="M24 24l6 4"/>'),
    "calendario": ('<rect x="7" y="10" width="34" height="31" rx="3"/><path d="M7 19h34M16 6v8M32 6v8"/>',
                   '<path class="ac m-pulsa" d="M18 30l4 4 8-9"/>'),
    "checklist": ('<path d="M12 8h24v34H12z"/><path d="M19 6h10v5H19z"/><path d="M24 20h8M24 28h8M24 36h6"/>',
                  '<path class="ac" d="M16 20l2 2 3-4M16 28l2 2 3-4"/>'),
    "camera": ('<path d="M6 16h9l3-5h12l3 5h9v24H6z"/><circle cx="24" cy="28" r="7"/>', '<path class="ac m-pisca" d="M36 21h3"/>'),
    "prateleira": ('<path d="M6 41V7M42 41V7M6 19h36M6 31h36M6 41h36"/>',
                   '<path class="ac m-sobe" d="M10 11h6v8h-6zM18 13h6v6h-6zM28 23h6v8h-6zM10 35h8v6h-8z"/>'),
    "caixa": ('<path d="M6 16l18-8 18 8v18l-18 8-18-8z"/><path d="M6 16l18 8 18-8M24 24v18"/>', '<path class="ac" d="M15 12l18 8"/>'),
    "etiqueta": ('<path d="M24 6h16v16L22 40 6 24z"/>', '<circle class="ac m-balanca" cx="33" cy="13" r="3"/>'),
    "olho": ('<path d="M4 24s7-12 20-12 20 12 20 12-7 12-20 12S4 24 4 24z"/>', '<circle class="ac m-pisca" cx="24" cy="24" r="5.5"/>'),
    "alvo": ('<circle cx="22" cy="26" r="15"/><circle cx="22" cy="26" r="8"/>', '<path class="ac m-sobe" d="M22 26L40 8M34 8h6v6"/>'),
    "balao": ('<path d="M6 10h36v22H20l-8 8v-8H6z"/>', '<circle class="ac m-pulsa" cx="17" cy="21" r="2"/><circle class="ac m-pulsa" cx="24" cy="21" r="2"/><circle class="ac m-pulsa" cx="31" cy="21" r="2"/>'),
    "conversa": ('<path d="M4 8h24v15H13l-5 5v-5H4z"/><path d="M32 18h12v14h-4v5l-5-5h-11v-6"/>', '<path class="ac m-pulsa" d="M10 15h12"/>'),
    "lampada": ('<path d="M17 30c-3-2-6-6-6-11a13 13 0 0 1 26 0c0 5-3 9-6 11v5H17z"/><path d="M18 40h12"/>',
                '<path class="ac m-pulsa" d="M24 2v3M7 8l2 2M41 8l-2 2M2 20h3M43 20h3"/>'),
    "alerta": ('<path d="M24 5l20 36H4z"/>', '<path class="ac m-pisca" d="M24 18v11M24 34v1"/>'),
    "certo": ('<circle cx="24" cy="24" r="18"/>', '<path class="ac" d="M15 25l6 6 12-13"/>'),
    "errado": ('<circle cx="24" cy="24" r="18"/>', '<path class="ac" d="M17 17l14 14M31 17L17 31"/>'),
    "tablet": ('<rect x="9" y="5" width="30" height="38" rx="3"/><path d="M21 38h6"/>', '<path class="ac m-varre" d="M15 13h18M15 19h12M15 25h15"/>'),
    "wobbler": ('<path d="M6 40h36M10 40v-4h28v4"/><path d="M24 36V24"/>', '<g class="m-balanca"><circle class="ac" cx="24" cy="15" r="9"/></g>'),
    "display": ('<path d="M12 42V12h24v30M12 22h24M12 32h24"/>', '<path class="ac m-sobe" d="M10 4h28v8H10z"/>'),
    "ilha": ('<path d="M4 26l20-8 20 8-20 8z"/><path d="M4 26v8l20 8 20-8v-8M24 34v8"/>', '<path class="ac m-sobe" d="M16 20v-8h4v6M26 18V9h4v10"/>'),
    "seta-chao": ('<ellipse cx="24" cy="32" rx="19" ry="9"/>', '<path class="ac m-varre" d="M15 33h16M26 28l6 5-6 5"/>'),
    "cartaz": ('<rect x="9" y="5" width="30" height="38" rx="1"/><path d="M15 34h18M15 38h12"/>', '<path class="ac m-pulsa" d="M15 11h18v17H15z"/>'),
    "carrinho": ('<path d="M3 7h6l5 24h24l4-16H12"/>', '<circle class="ac m-gira" cx="18" cy="38" r="3"/><circle class="ac m-gira" cx="34" cy="38" r="3"/>'),
    "escudo": ('<path d="M24 4l16 6v12c0 10-7 17-16 21C15 39 8 32 8 22V10z"/>', '<path class="ac" d="M17 23l5 5 9-10"/>'),
    "comprimido": ('<rect x="5" y="17" width="38" height="14" rx="7" transform="rotate(-35 24 24)"/>', '<path class="ac m-pulsa" d="M18 16l12 16"/>'),
    "frasco": ('<path d="M17 18h14l3 6v18H14V24z"/><path d="M20 18v-6h8v6M28 9h7v4"/>', '<path class="ac m-pisca" d="M38 8l3-2M38 12h4M38 16l3 2"/>'),
    "casa": ('<path d="M6 22L24 7l18 15M10 19v22h28V19"/>', '<path class="ac m-pulsa" d="M20 41V30h8v11"/>'),
    "pessoa": ('<circle cx="24" cy="14" r="7"/><path d="M10 42c1-9 7-14 14-14s13 5 14 14"/>', '<path class="ac" d="M20 34l4 4 4-4"/>'),
    "pessoas": ('<circle cx="17" cy="16" r="6"/><path d="M5 40c1-8 6-12 12-12s11 4 12 12"/>', '<circle class="ac m-sobe" cx="34" cy="14" r="5"/><path class="ac" d="M31 26c5 0 10 4 11 12"/>'),
    "grafico": ('<path d="M6 6v36h36"/>', '<path class="ac m-cresce" d="M13 36V26M22 36V18M31 36V22M40 36V10"/>'),
    "mapa": ('<path d="M4 12l12-5 16 5 12-5v29l-12 5-16-5-12 5z"/><path d="M16 7v29M32 12v29"/>', '<path class="ac m-sobe" d="M24 18c0-3 2-5 4-5s4 2 4 5c0 3-4 7-4 7s-4-4-4-7z"/>'),
    "lupa": ('<circle cx="20" cy="20" r="12"/><path d="M29 29l12 12"/>', '<path class="ac m-varre" d="M14 20h12"/>'),
    "estrela": ('<path d="M24 5l5.6 12.2 13.4 1.4-10 9 2.9 13.2L24 34l-11.9 6.8 2.9-13.2-10-9 13.4-1.4z"/>', '<circle class="ac m-pulsa" cx="24" cy="24" r="4"/>'),
    "coracao": ('<path d="M24 41S6 30 6 17a9 9 0 0 1 18-3 9 9 0 0 1 18 3c0 13-18 24-18 24z"/>', '<path class="ac m-pulsa" d="M14 24h6l3-5 4 9 3-4h5"/>'),
    "cao": ('<path d="M14 18c-6-2-9 4-7 10 3 0 5-2 6-4M34 18c6-2 9 4 7 10-3 0-5-2-6-4"/><path d="M14 18c2-5 6-7 10-7s8 2 10 7v10c0 7-5 11-10 11s-10-4-10-11z"/>',
            '<path class="ac m-pisca" d="M19 25v1M29 25v1"/><path class="ac" d="M22 32h4l-2 2z"/>'),
    "gato": ('<path d="M12 22L10 6l10 7c3-1 5-1 8 0l10-7-2 16c2 3 2 6 2 8 0 7-6 11-14 11S10 37 10 30c0-2 0-5 2-8z"/>',
             '<path class="ac m-pisca" d="M18 27v2M30 27v2"/><path class="ac" d="M22 33h4l-2 2zM4 31h8M4 35h8M36 31h8M36 35h8"/>'),
    "seta": ('<path d="M6 24h32"/>', '<path class="ac m-varre" d="M30 15l9 9-9 9"/>'),
    "mao": ('<path d="M17 24V9a3 3 0 0 1 6 0v12V6a3 3 0 0 1 6 0v15V9a3 3 0 0 1 6 0v18c0 9-5 15-12 15-5 0-8-3-11-8l-5-8a3 3 0 0 1 5-3l5 5z"/>', '<path class="ac m-pulsa" d="M8 6l3 3M4 14h4"/>'),
    "folha": ('<path d="M10 38C8 22 18 8 40 8c0 22-14 32-30 30z"/>', '<path class="ac m-sobe" d="M10 38L28 20"/>'),
    "moeda": ('<circle cx="24" cy="24" r="17"/>', '<path class="ac m-gira" d="M29 17c-1-2-3-3-5-3-3 0-5 2-5 4s2 3 5 4 5 2 5 5-2 4-5 4c-3 0-5-1-6-3M24 11v3M24 34v3"/>'),
    "pin": ('<path d="M24 44S10 29 10 18a14 14 0 0 1 28 0c0 11-14 26-14 26z"/>', '<circle class="ac m-sobe" cx="24" cy="18" r="5"/>'),
}


def icone(nome, cls="", tam=None, titulo=""):
    tr, ac = I[nome]
    t = f' width="{tam}" height="{tam}"' if tam else ""
    rotulo = f'<title>{titulo}</title>' if titulo else ""
    # pathLength=1 deixa o efeito de desenhar uniforme em todos os traços
    tr = tr.replace("<path ", '<path pathLength="1" ').replace("<circle ", '<circle pathLength="1" ').replace("<rect ", '<rect pathLength="1" ').replace("<ellipse ", '<ellipse pathLength="1" ')
    return (f'<svg class="ic {cls}" viewBox="0 0 48 48"{t} fill="none" stroke-linecap="round" stroke-linejoin="round" '
            f'{"role=img" if titulo else "aria-hidden=true"}>{rotulo}<g class="tr">{tr}</g><g class="acs">{ac}</g></svg>')


CSS = """
.ic{--tr:var(--navy);--ac:var(--verde);overflow:visible}
.ic .tr>*{stroke:var(--tr);stroke-width:2.4}
.ic .acs>*,.ic .acs g>*{stroke:var(--ac);stroke-width:2.8;fill:none}
.ic .acs circle.ac,.ic .acs .ac[d$="z"]{fill:var(--ac);fill-opacity:.18}
.slide.viu .ic .tr>*{stroke-dasharray:1;stroke-dashoffset:1;animation:icRisca .9s cubic-bezier(.6,.05,.3,1) forwards;animation-delay:calc(var(--d,0) * 1s + .25s)}
.slide.viu .ic .acs{opacity:0;animation:icAcento .5s cubic-bezier(.2,1.4,.4,1) forwards;animation-delay:calc(var(--d,0) * 1s + .85s);transform-origin:24px 24px;transform-box:view-box}
.slide.viu .ic .m-gira{transform-box:fill-box;transform-origin:center;animation:icGira 6s linear infinite 1.4s}
.slide.viu .ic .m-balanca{transform-box:view-box;transform-origin:24px 24px;animation:icBalanca 2.6s ease-in-out infinite 1.4s}
.slide.viu .ic .m-pulsa{transform-box:fill-box;transform-origin:center;animation:icPulsa 2.4s ease-in-out infinite 1.4s}
.slide.viu .ic .m-sobe{animation:icSobe 2.8s ease-in-out infinite 1.4s}
.slide.viu .ic .m-pisca{animation:icPisca 3.6s steps(1) infinite 1.6s}
.slide.viu .ic .m-varre{animation:icVarre 2.2s ease-in-out infinite 1.4s}
.slide.viu .ic .m-cresce{stroke-dasharray:30;stroke-dashoffset:30;animation:icCresce 1.2s ease-out forwards 1s}
@keyframes icRisca{to{stroke-dashoffset:0}}
@keyframes icAcento{from{opacity:0;transform:scale(.6)}to{opacity:1;transform:none}}
@keyframes icGira{to{transform:rotate(360deg)}}
@keyframes icBalanca{0%,100%{transform:rotate(-7deg)}50%{transform:rotate(7deg)}}
@keyframes icPulsa{0%,100%{transform:scale(1)}50%{transform:scale(1.18)}}
@keyframes icSobe{0%,100%{transform:translateY(0)}50%{transform:translateY(-2.5px)}}
@keyframes icPisca{0%,92%{opacity:1}94%{opacity:.1}96%{opacity:1}}
@keyframes icVarre{0%,100%{transform:translateX(0)}50%{transform:translateX(3px)}}
@keyframes icCresce{to{stroke-dashoffset:0}}
@media (prefers-reduced-motion:reduce){.slide.viu .ic *{animation:none!important;stroke-dashoffset:0!important;opacity:1!important}}
@media print{.ic *{animation:none!important;stroke-dashoffset:0!important;opacity:1!important}}
"""

if __name__ == "__main__":
    # folha de prova com todos os ícones
    import os
    html = "".join(f'<figure>{icone(n, tam=72)}<figcaption>{n}</figcaption></figure>' for n in I)
    out = f"""<!doctype html><meta charset=utf-8><style>:root{{--navy:#072047;--verde:#10AD31}}body{{font:14px sans-serif;display:grid;grid-template-columns:repeat(8,1fr);gap:18px;padding:30px}}figure{{margin:0;text-align:center}}{CSS}</style><section class="slide viu" style="display:contents">{html}</section>"""
    open(os.path.join(os.path.dirname(__file__), "icones-prova.html"), "w").write(out)
    print(len(I), "ícones")
