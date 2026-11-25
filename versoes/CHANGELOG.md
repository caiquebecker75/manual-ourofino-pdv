# Histórico de versões · Guia de Execução Ourofino Pet

Regra do projeto (desde 24/11/2026): antes de qualquer ajuste grande, a versão publicada é
congelada aqui, para a gente conseguir consultar ou voltar atrás.

Cada versão congelada fica navegável no próprio site:
`https://projetos.75lab.com.br/manual-ourofino-pdv/versoes/<pasta ou arquivo>`

Como voltar para uma versão: copie o conteúdo dela para a raiz e dê push.
No git, cada versão também tem uma tag (`git checkout <tag> -- .` restaura os arquivos).

| Data | Versão | Onde está | Tag | O que era |
|------|--------|-----------|-----|-----------|
| 2026-11-24 | v1 | `2026-11-24_v1_pre-reuniao-bianca.html` | `v1-pre-reuniao` | Versão entregue antes da 1ª rodada de feedback da cliente (reunião de 19/11). 15 capítulos, paleta creme + verde-floresta + lima, atlas de produtos, PDF em formato livro. |
| 2026-11-24 | v2 | `2026-11-24_v2/` | `v2` | Reestruturação pedida na reunião de 19/11 (detalhes abaixo). Imagens 3D feitas no Blender. |
| 2026-11-24 | v3 | `2026-11-24_v3/` | `v3` | Visual refeito no estilo do guia de referência mostrado na reunião (detalhes abaixo). |
| 2026-11-24 | v4 | `2026-11-24_v4/` | `v4` | Guia em formato de slides, conteúdo reescrito na ordem do guia de referência, marca oficial Ourofino (detalhes abaixo). |
| 2026-11-24 | v5 | `2026-11-24_v5/` | `v5` | A v4 condensada em 49 slides, o mesmo número de páginas do guia de referência (detalhes abaixo). |

## v5 · o que mudou em relação à v4

Pedido do Caique em 24/11: 348 slides era grande demais para alguém ler. Reduzir para a mesma quantidade de páginas do guia de referência mostrado no vídeo (49).

- **Tamanho:** de 348 para 49 slides. Abertura (capa, Serafina, como usar, sumário), nove capítulos com capa própria e fechamento (considerações da Serafina, checklist, teste final e contracapa).
- **Capítulos:** 1 contato no PDV (antes, durante e depois, com botões na capa), 2 trade marketing, 3 básico da gôndola, 4 materiais de PDV, 5 cross, 6 ponto natural e ponto extra, 7 relacionamento, postura e quem decide, 8 CBV e produtos heróis, 9 prateleira ideal.
- **Juntado:** objetivo do guia foi para a abertura; relacionamento, postura e "conhecendo a loja" viraram um capítulo; CBV e heróis viraram um capítulo; glossário virou um slide de palavras do trade; checklist e teste final cabem num slide cada.
- **Slides novos:** galeria de materiais (11 materiais em 2 slides, com foto de cada um), grade de produtos heróis com a frase de balcão, checklist em 3 colunas, teste final com uma pergunta por vez e placar, contracapa.
- **Serafina:** continua na capa de abertura, na fala inicial e final, nos erros comuns e na faixa verde "Dica da Serafina" no pé de alguns slides.
- **Mantido da v4:** marca oficial, ícones animados, capas diferentes por capítulo, fotos do pack, dados com fonte verificada, modo Revisão com as notas para a Ourofino validar.
- **Gerador:** `python3 tools/deck/build_deck.py`, com texto em `conteudo-v5/`. O texto completo da v4 continua em `conteudo-v4/` e na tag `v4`.

## v4 · o que mudou em relação à v3

Pedido do Caique em 24/11, depois de ver a v3: formato de slide (não landing page), ícones animados, capa diferente por capítulo, texto mais explicativo e mais profundo, ilustração sem fundo, nada de layout com cara de IA, seguir o guia de marca da Ourofino, seguir a ordem do PDF de referência e apresentar a Serafina.

- **Formato:** deck de 348 slides. No computador, palco 16:9 com setas, teclado e índice; no celular, uma tela vertical por slide; PDF com um slide por página.
- **Ordem:** a do guia de referência (Elanco) mostrado na reunião, com os ajustes da cliente: Serafina, objetivo, contato no PDV, fundamentos, gôndola, materiais, cross, ponto extra, relacionamento, postura, loja e quem decide, CBV, heróis por categoria, prateleira ideal e considerações finais. Depois vêm o checklist, o glossário e o teste final.
- **Conteúdo:** reescrito do zero em slides. Cada conceito traz o que é, o mecanismo, como fazer e um exemplo de loja pet. Os dados têm fonte verificada e as notas a validar (64) ficam no modo Revisão.
- **Marca:** segue o Guia de aplicação de marca Ourofino Saúde Animal v2.0, de 2026.
  - Cores sólidas oficiais.
  - Títulos em Young Serif, no lugar da Roca One, que é paga; texto em Poppins, a mesma que o site da Ourofino usa no lugar da Gilroy.
  - Logos oficiais em vetor e a faixa de animais geométricos da contracapa oficial.
  - A forma de "folha" com um canto reto em botões, balões e máscaras.
- **Imagens:**
  - pack de 41 fotos reais de shooting de cães e gatos (Unsplash/Pexels, licença comercial gratuita; créditos em `Downloads/ourofino-fotos/CREDITOS.csv`), recortadas sem fundo;
  - a Serafina ilustrada em 8 poses, sem fundo;
  - 3 cenas ilustradas recortadas;
  - as fotos de loja do ChatGPT com embalagens reais.
- **Capas:** uma diferente por capítulo, em 8 composições (foto lateral, pet recortado sobre o número, gato espiando, foto na forma de folha, dupla, faixa geométrica, tipográfica, Serafina).
- **Ícones:** 45 ícones próprios animados, que se desenham quando o slide entra e têm um movimento contínuo sutil.
- **Anti-clichê:** lista de padrões de layout com cara de IA em `tools/deck/NAO-FAZER.md`.
- **Gerador:** `python3 tools/deck/build_deck.py`, com texto em `conteudo-v4/`.

## v3 · o que mudou em relação à v2

Pedido do Caique em 24/11, depois de ver a v2: trocar as imagens 3D por imagens geradas no ChatGPT, criar as ilustrações e usar fotos de shooting de animais, como no guia mostrado no vídeo da reunião.

- Capa e aberturas de capítulo com fotos de estúdio de cães e gatos recortadas sobre a faixa diagonal azul, número grande e título manuscrito.
- Personagem ilustrada (promotora de polo verde, em 3D estilizado) em 8 poses: dá as dicas em balão de fala, aparece nos erros comuns, nos testes, no sumário e no checklist. Provisória até chegar a arte da turma do bite.
- 4 cenas ilustradas com a personagem: chegada ao balcão, reposição com FIFO, conversa com a gerente e o tutor na gôndola.
- 21 fotos de loja refeitas no ChatGPT a partir das cenas 3D, com as embalagens e o logotipo reais: antes e depois, ponto extra certo e errado (pares alinhados para o comparador), zonas de altura, prateleira ideal e cada material de PDV.
- Imagens geradas: `tools/imagens_ia.py` (lista e prompts) e `tools/chatgpt_img.py`; recorte de fundo em `tools/recorte.py`.

## v2 · o que mudou em relação à v1

Fonte dos pedidos: `../BRIEFING-REUNIAO-19-11.md`.

**Estrutura**
- Sumário tradicional por partes (Abertura, Entender, A visita, Na gôndola, Materiais e cross, Produtos, Postura, Fechamento) e trilhas de leitura clicáveis por papel.
- 13 capítulos + glossário A a Z, checklist da visita e teste final com 10 situações.
- Entraram: objetivo do guia, antes/durante/depois da visita, script de relacionamento em loja, quem decide em cada tipo de loja, ponto natural x ponto extra, prateleira ideal, cross merchandising separado de cross selling, CBV e fichas dos 7 produtos heróis.
- Saíram: papéis e responsabilidades, e-commerce, incentivos, produto âncora, negociação e a classificação estímulo/atração/conversão.

**Texto**
- Reescrito para quem está começando ("o óbvio precisa ser dito"), em segunda pessoa, sem jargão sem explicação.
- Corrigido o erro de categoria: higiene e beleza do pet fica fora da farmácia; nada de "execução cosmética".
- Linguagem de promotor: "avise o seu supervisor" no lugar de "faço/apoio/escalo".
- 25 notas "Para a Ourofino validar" visíveis no botão Revisão.

**Visual**
- Paleta oficial Ourofino (azul-marinho, verde, azul e ciano) no lugar do reskin lima.
- Loja 3D fotorrealista renderizada no Blender: 21 cenas de execução e materiais + 7 aberturas de capítulo.
- Diagramas desenhados para o guia: caminho do produto, planta da loja, mapa de cross, visita em 3 momentos, FIFO, blocagem, CBV.
- Comparadores "arraste para ver" (antes/depois e ponto extra errado/certo), marcações nas fotos, testes rápidos, checklist que salva no celular, glossário com busca.
- PDF em A4 paisagem, duas colunas.

**Pendente da Ourofino** (ver notas do modo Revisão): arte da turma do bite, lista oficial de heróis e pares de cross, estudo de quem decide por PDV, lista de MPDV disponíveis, ciclo de vendas/canais.
