# Briefing Visual — Manual de Execução em PDV · Ourofino Pet

Este documento tem duas partes:
1. **Briefing de imagens** — tudo que precisa ser gerado por IA externa (ou fornecido pelo cliente), com prompt por item.
2. **Plano de diagramação por capítulo** — o arquétipo de layout de cada capítulo.

> Legenda de tipo:
> **[FOTO]** você gera na IA externa · **[SIMULAÇÃO/PLANOGRAMA]** você gera na IA externa · **[OFICIAL]** cliente fornece (fotos de produto) · **[SVG]** eu construo em código (não precisa gerar).

---

## BLOCO-ESTILO (cole junto de todo prompt [FOTO])

> Fotografia publicitária realista e editorial, ambiente de pet shop brasileiro moderno, limpo e muito bem iluminado; luz natural suave; composição profissional; sensação de cuidado, confiança e organização; detalhes com verde vibrante (#10AD31) e azul-marinho (#072047) da marca; foto real (não ilustração); altíssima resolução.
> **Evitar:** textos ou logotipos legíveis/inventados, aparência plástica/artificial, cores berrantes fora da paleta, bagunça (exceto quando o item pedir).

*(Se usar Midjourney, traduza os termos de estilo para inglês e acrescente o `--ar` indicado.)*

---

## 1. Briefing de imagens

### CAPA
- **C00 · Herói da capa** — [FOTO] `--ar 16:9`
  Corredor amplo de um pet shop moderno e bem iluminado; prateleiras organizadas de produtos de saúde animal; ao fundo, uma promotora de uniforme com tablet conferindo a gôndola; foco nítido, profundidade de campo suave. *(+ BLOCO-ESTILO)*

### Cap. 1 — Boas-vindas
- **C01-01 · Capa do capítulo** — [FOTO] `--ar 16:9`
  Promotor(a) de uniforme sorrindo na entrada de um pet shop, credencial no pescoço, prancheta/tablet na mão, luz da manhã; acolhedor. *(+ BLOCO-ESTILO)*
- Mapa de navegação / trilhas de leitura → **[SVG]**

### Cap. 2 — Empresa, cultura e postura
- **C02-01 · Capa do capítulo** — [FOTO] `--ar 3:2`
  Retrato de meio corpo de promotor(a) profissional de uniforme, postura ereta e cordial, pet shop desfocado ao fundo. *(+ BLOCO-ESTILO)*
- **C02-02 · Tríptico "valores em ação"** — [FOTO] 3 imagens `--ar 1:1`
  (a) mãos limpando e alinhando embalagens na prateleira; (b) promotor cumprimentando um balconista com respeito; (c) promotor observando e esperando o momento certo para abordar. *(+ BLOCO-ESTILO)*

### Cap. 3 — Portfólio de produtos
- **C03-01 · Fotos de produto por linha** — [OFICIAL]
  Usar as imagens oficiais da Ourofino (PNG com fundo transparente). Não gerar por IA. Linhas: cuidados, prevenção/proteção, medicamentos, suplementos, ambiente, diagnóstico.
- **C03-02 · Capa do capítulo** — [FOTO] `--ar 16:9`
  Gôndola de farmácia pet completa e bem abastecida, produtos blocados por linha; visão frontal. *(+ BLOCO-ESTILO)*

### Cap. 4 — Conceitos de Trade
- **C04-01 · Ruptura (antes/depois)** — [SIMULAÇÃO] par `--ar 4:3`
  ANTES: gôndola com ruptura — espaços vazios, produtos tortos, sem etiqueta de preço. DEPOIS: a mesma gôndola cheia, alinhada, com etiquetas visíveis. *(+ BLOCO-ESTILO)*
- Fluxo sell-in → execução → sell-out → **[SVG]**

### Cap. 5 — Canais e jornadas
- **C05-01 · Capa do capítulo** — [FOTO] `--ar 16:9`
  Vista ampla de um pet shop movimentado, shoppers circulando, área de farmácia visível ao fundo. *(+ BLOCO-ESTILO)*
- **C05-02 · Três formatos de canal** — [FOTO] 3 imagens `--ar 4:3`
  (a) pet shop de autosserviço; (b) pet shop com clínica; (c) clínica com pet shop (serviço no centro, farmácia complementar). *(+ BLOCO-ESTILO)*
- Mapa de jornada do shopper com áreas quentes → **[SVG]**

### Cap. 6 — Sortimento e farmácia P/M/G
- **C06-01 · Planograma P / M / G** — [PLANOGRAMA] 3 imagens `--ar 16:9`
  Planograma fotorrealista de farmácia pet em 3 portes: **P** (foco, poucas prateleiras), **M** (complementar), **G** (portfólio ampliado). Vista frontal esquemática, produtos organizados por linha e prioridade, etiquetas de preço. *(+ BLOCO-ESTILO)*
- **C06-02 · Capa do capítulo** — [FOTO] `--ar 3:2`
  Close de uma prateleira de farmácia pet bem sortida e organizada. *(+ BLOCO-ESTILO)*

### Cap. 7 — Execução, gôndola e planograma
- **C07-01 · Gôndola ANTES / DEPOIS (imagem-estrela)** — [SIMULAÇÃO] par `--ar 4:3`
  ANTES: gôndola de farmácia pet bagunçada — ruptura, produtos tortos, sem preço, categorias misturadas. DEPOIS: a mesma gôndola blocada por linha, alinhada, com preço, produtos prioritários no campo de visão. *(+ BLOCO-ESTILO)*
- **C07-02 · Planograma comentado** — [PLANOGRAMA] `--ar 16:9`
  Planograma fotorrealista mostrando blocagem por categoria, individual ao lado do combo e sequência por porte/peso. *(+ BLOCO-ESTILO)*
- **C07-03 · Detalhes de execução** — [FOTO] 3 imagens `--ar 1:1`
  (a) mãos aplicando FIFO (girando validade); (b) limpando/alinhando embalagem; (c) conferindo/repondo etiqueta de preço. *(+ BLOCO-ESTILO)*

### Cap. 8 — Cross merchandising
- **C08-01 · Capa do capítulo** — [FOTO] `--ar 16:9`
  Clip strip com produtos de higiene pendurado próximo à área de areia/tapetes; cross discreto e organizado. *(+ BLOCO-ESTILO)*
- **C08-02 · Cross por material** — [SIMULAÇÃO] `--ar 4:3`
  Stopper/cubo sinalizando categoria complementar, sem deslocar produto de valor da farmácia. *(+ BLOCO-ESTILO)*

### Cap. 9 — Materiais de PDV
- **C09-01 · Kit de mockups de MPDV** — [SIMULAÇÃO/MOCKUP] 6 imagens `--ar 1:1`
  Mockups fotorrealistas aplicados na loja: **wobbler**, **cubo**, **cartaz de vitrine**, **clip strip**, **stopper de gôndola**, **display de chão**. Cada um bem instalado, sem cobrir preço. *(+ BLOCO-ESTILO)*
- **C09-02 · Capa do capítulo** — [FOTO] `--ar 16:9`
  Gôndola com materiais de PDV bem instalados e organizados. *(+ BLOCO-ESTILO)*

### Cap. 10 — Papel do promotor
- **C10-01 · Capa do capítulo** — [FOTO] `--ar 3:2`
  Promotor fotografando a gôndola com o celular para registrar evidência; prancheta na outra mão. *(+ BLOCO-ESTILO)*
- **C10-02 · Alinhamento com a loja** — [FOTO] `--ar 4:3`
  Promotor conversando e alinhando com o responsável da loja, postura respeitosa. *(+ BLOCO-ESTILO)*

### Cap. 11 — Rotina ProTrade
- **C11-01 · Capa do capítulo** — [FOTO] `--ar 16:9`
  Promotor chegando à loja com mochila/kit de materiais, checando o roteiro no celular. *(+ BLOCO-ESTILO)*
- Linha do tempo da visita (2h vs 6h) → **[SVG]**

### Cap. 12 — Abordagem e scripts
- **C12-01 · Capa do capítulo** — [FOTO] `--ar 3:2`
  Promotor conversando de forma cordial com um balconista atrás do balcão. *(+ BLOCO-ESTILO)*
- **C12-02 · Abordagem ao gerente** — [FOTO] `--ar 4:3`
  Promotor mostrando a organização de uma linha para o gerente da loja. *(+ BLOCO-ESTILO)*

### Cap. 13 — Conduta profissional
- **C13-01 · Capa do capítulo** — [FOTO] `--ar 3:2`
  Promotor uniformizado com jaleco, postura profissional e cordial no corredor da loja. *(+ BLOCO-ESTILO)*

### Cap. 14 — Indicadores e score
- **C14-01 · Capa do capítulo** — [FOTO] `--ar 16:9`
  Mãos segurando tablet/celular com um checklist/score aberto; gôndola desfocada ao fundo. *(+ BLOCO-ESTILO)*
- Dashboard / scorecard visual → **[SVG]**

### Cap. 15 — Anexos práticos
- **C15-01 · Capa do capítulo** — [FOTO] `--ar 16:9`
  Checklist impresso A5 sendo preenchido no campo, apoiado na prateleira; caneta na mão. *(+ BLOCO-ESTILO)*

---

## 2. Plano de diagramação por capítulo (layouts diferenciados)

| Cap | Tema | Arquétipo de layout | Cor de destaque | Infográfico principal (SVG) |
|----|------|---------------------|-----------------|------------------------------|
| 1 | Boas-vindas | Editorial de abertura + mapa de uso | Verde | Mapa de navegação / trilhas |
| 2 | Cultura e postura | Manifesto + tríptico "valores em ação" | Navy | Valores → atitude |
| 3 | Portfólio | Catálogo / galeria de fichas | Multicolor por linha | Grade de linhas |
| 4 | Conceitos de trade | Didático / glossário + fluxo | Ciano | Sell-in → sell-out |
| 5 | Canais e jornadas | Mapa + comparação de formatos | Verde | Jornada do shopper c/ áreas quentes |
| 6 | Sortimento P/M/G | Matriz + planogramas | Azul | Matriz de mix P/M/G |
| 7 | Execução / gôndola | Passo a passo + antes/depois | Verde | Hierarquia de execução + planograma |
| 8 | Cross merchandising | Conexões / pares de categoria | Ciano | Diagrama de associações + risco |
| 9 | Materiais de PDV | Fichas técnicas de material | Azul | Mapa de melhor local |
| 10 | Papel do promotor | Quadrante RACI | Navy | Faço / apoio / escalo / não faço |
| 11 | Rotina ProTrade | Timeline horizontal | Verde | Linha do tempo 2h vs 6h |
| 12 | Abordagem / scripts | Diálogos / cards de conversa | Azul | Diga assim / evite dizer |
| 13 | Conduta | Código sempre / nunca | Navy | Dois blocos + situações |
| 14 | Indicadores / score | Dashboard | Verde | Scorecard + KPIs |
| 15 | Anexos | Toolkit / índice de ferramentas | Ciano | Grade de materiais destacáveis |

Cada capítulo abre com uma **página-capa (divisória)** full-bleed: número gigante, tema, foto-herói e um bloco "Neste capítulo você vai dominar…".
