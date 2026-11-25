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
| 2026-11-24 | v6 | `2026-11-24_v6/` | `v6` | Ensaio fotográfico novo e diagramação de livro, com uma composição diferente em cada slide (detalhes abaixo). |
| 2026-11-25 | v7 | `2026-11-25_v7/` | `v7` | Capítulo novo com os 10 produtos de cada categoria em fichas CBV: 58 slides (detalhes abaixo). |
| 2026-11-25 | v8 | `2026-11-25_v8/` | `v8` | Capas novas, revisão de texto sobre texto, texto mais explicado, clínica e categoria, slides do cap. 1 mais lúdicos e FIFO animado: 60 slides (detalhes abaixo). |
| 2026-11-25 | v9 | `2026-11-25_v9/` | `v9` | Mais 14 slides lúdicos (álbum, estrada, convite, placas, prateleira desenhada e outros) e o guia dividido em 5 etapas para a Ourofino aprovar, com cronograma (detalhes abaixo). |

## v9 · o que mudou em relação à v8

Pedidos do Caique em 25/11: deixar os outros slides mais lúdicos, como a chegada e os oito passos, e montar um cronograma com a entrega quebrada por etapas, já com o material separado para a cliente aprovar.

- **14 slides de texto viraram brincadeira visual:**
  - Antes de sair: o kit da visita com cada peça escrita à mão na foto, e os cinco passos numa prancheta que vai ticando.
  - Depois da visita: os quatro passos chegam como lembretes na tela de um celular.
  - 76%: o número pendurado num wobbler que balança na beira da prateleira.
  - O caminho do produto: uma estrada com a fábrica, o distribuidor, a loja e a casa do tutor, placas de sell-in e sell-out, um caminhão que anda e a sacola indo para casa.
  - As palavras do trade: seis figurinhas de álbum.
  - O básico: quatro carimbos batidos em ordem.
  - Ruptura: os 100 compradores viraram bonequinhos.
  - Dois tipos de cross: desenho do wobbler que muda de corredor, o par Top Dog e Herbalvet, e o teste da frase como frase de completar.
  - Você é convidado na loja: as regras da casa num convite tirado do envelope.
  - Três frases: a gerente fala em balões, com a dica da Serafina no balcão.
  - Quem decide: três fachadas de loja (petshop, petshop com clínica, clínica com petshop) e quem responde por cada decisão.
  - Postura em campo: placas de trânsito de "sempre" e de "proibido".
  - Pode e não pode dizer: balões de fala certos e errados, com o gato perguntando "posso falar isso?".
  - Cinco regras da prateleira ideal: farmácia desenhada com as cinco regras marcadas.
- **Aprovação por etapas:** cronograma em `cronograma/` com as 5 etapas, a reta final, o que precisamos da Ourofino e o retorno de cada etapa.
- **Apresentação da etapa 1** em `apresentacao/etapa-1/`: só as 10 páginas do guia que entram na etapa, sem nenhuma tela a mais, em formato de apresentação (tela cheia, uma por vez). Datas, pontos para validar e próximos passos ficam só no cronograma. O link fica no cartão da etapa no cronograma; as próximas etapas ganham a apresentação delas no dia em que forem mostradas (`apresentacao=True` em ETAPAS no `tools/v6/etapas.py`). O cronograma não mostra mais as telas de cada etapa.

## v8 · o que mudou em relação à v7

Pedidos do Caique em 25/11, todos na mesma rodada.

- **Capas dos capítulos refeitas:** cada capa virou uma abertura de livro. O texto fica num painel de cor sólida (azul-marinho, papel, verde ou azul) e a foto ocupa o outro lado, com o bicho inteiro e nada escrito por cima. O painel traz o número grande, o nome da parte, o tempo de leitura, o título, a abertura e o "Neste capítulo" com as páginas de cada slide.
- **Texto sobre texto:** varredura automática no PDF (computador) e na página (celular e tablet em pé). Saíram os números e letras gigantes que ficavam atrás do texto (o "01" e o "10" das capas, o "Aa" do dicionário, as aspas gigantes da carta). Legendas de foto não encostam mais no número da página nem no cabeço. No comparador do ponto extra, as etiquetas ficaram do lado esquerdo dos pinos e não são mais cortadas pela linha. No mapa dos cruzamentos, os pinos 4 e 5 saíram de cima do rótulo. No celular, a tabela de quem decide vira cartões e o mapa e as marcações da prateleira não são mais cortados.
- **Texto mais explicado:** 29 trechos reescritos para quem começa do zero. "Os quatro básicos" virou "O básico: 4 coisas para conferir", com o porquê de cada item; termos como wobbler, spot on, gôndola, ponto extra, frente e blocagem ganharam explicação no lugar onde aparecem pela primeira vez; títulos vagos ficaram diretos.
- **Capítulo 1 mais lúdico:** "A chegada, palavra por palavra" virou conversa em balões com a cena da Serafina cumprimentando o balconista atrás do balcão; os balões entram um por vez. "Os oito passos" virou tabuleiro de jogo, com caminho, casas coloridas, início e chegada.
- **FIFO animado:** a caixa da frente sai com o tutor, as outras andam para a frente e o lote novo entra por trás, em ciclo.
- **Duas páginas novas (os pontos que estavam parciais no de-para com o guia de referência):** "Na clínica: o caminho do tutor" (cap. 4), com planta de clínica, caminho de chegada e de saída animado e os pontos de material; e "Pense na categoria inteira" (abre o cap. 10), com o que o tutor e a loja ganham e como falar disso com balconista, gerente e tutor. Foto nova do shih-tzu na cesta.

## v7 · o que mudou em relação à v6

Pedido do Caique em 25/11: faltava um capítulo com os 10 principais produtos de cada categoria, dentro do conceito CBV, mesmo que o guia ganhasse slides.

- **Capítulo 9 novo, "Os 10 de cada categoria":** 33 produtos da Ourofino Pet nas categorias do site da marca. Prevenção e proteção (6), Suplementos (10), Medicamentos (10), Cuidados (5) e Desinfecção (2). As categorias com menos de dez produtos no portfólio entram completas. Os testes de diagnóstico Conclue ficam de fora porque são de uso na clínica.
- **Cada produto tem uma ficha CBV** (característica, benefício e vantagem), escrita a partir das páginas oficiais em ourofinopet.com, sem dose e sem promessa de resultado. Selo "herói" liga o produto ao capítulo 8; selo "com receita" marca os medicamentos, que entram com a regra de conferir a receita e encaminhar a dúvida ao veterinário.
- **Nove páginas, cada uma com composição própria:** capa (schnauzer com sacola), como ler as fichas (ficha de exemplo com chamadas e índice das categorias com página), grade de seis cartões, prateleira da linha Snacks, tabela de suplementos com foto, bula dos medicamentos em duas colunas com carimbo, quadro azul-marinho com as regras do balcão, ritual do banho da linha Bris em três passos e página dupla da desinfecção.
- **Embalagens oficiais:** 27 fotos baixadas do site da Ourofino Pet (originais no HD em `Downloads/ourofino-referencia/embalagens`), sem o selo "nova embalagem", em `assets/img/pk/`.
- **Fotos novas:** capa do capítulo, gato na toalha, filhote no piso limpo e cão idoso, no mesmo ensaio da v6 (`tools/v6/ensaio.py`).
- **Renumeração:** Prateleira ideal passa a ser o capítulo 10 e o fechamento usa `cap11`. O teste final ganhou uma pergunta sobre a ficha CBV (10 perguntas).
- **Revisão:** duas notas novas para a Ourofino validar (ranking dos 10 de cada categoria e uso dos medicamentos no material do promotor). Total de 14.

## v6 · o que mudou em relação à v5

Pedido do Caique em 24/11: as imagens dos animais ficaram péssimas, os slides não estavam bonitos nem bem acabados; cada slide deve ser diferente do outro e visualmente incrível, como um livro com diagramação muito legal.

- **Fotos:** ensaio novo de 22 fotos gerado no ChatGPT, todas no mesmo estúdio e com a mesma luz. Os pets ficam em fundos nas cores da Ourofino (azul-marinho, verde, azul, ciano, cinza e branco), com sombra real no chão e espaço planejado para o título. Entram sangradas, sem recorte. O ensaio inclui ainda cenas de loja e de casa (kit da visita, foto da gôndola, tutora no balcão, veterinária, filhote no tapete, cão no passeio). Lista e prompts em `tools/v6/ensaio.py`; originais em `assets/ia/v6-*.png` (fora do git); páginas usam `assets/img/v6/`.
- **Diagramação:** cada um dos 49 slides tem composição própria (`@layout` no conteúdo), com recursos de livro:
  - cabeço com o nome do capítulo e fólio no canto externo, alternando página par e ímpar;
  - capitular, carta assinada pela Serafina, citação em destaque, legenda de figura numerada e nota de rodapé para a fonte dos dados;
  - sumário com pontilhado e páginas, glossário como página de dicionário, roteiro da chegada em formato de diálogo;
  - trilha dos oito passos, gráfico de unidades da ruptura, régua das alturas da gôndola, escada do ponto extra, degraus do CBV;
  - catálogo e tira de fotos dos materiais, produtos em cartões e em linhas, "Sempre" e "Nunca" em letras grandes.
- **Capas:** foto sangrada diferente em cada capítulo, com o número em quatro estilos (gigante, contorno, linha, filete) e o texto no espaço vazio da foto. A abertura traz o nome da Serafina gigante com ela na frente das letras.
- **Conteúdo:** o mesmo da v5, com ajustes pequenos para a nova página (por exemplo, o dado completo da ruptura: 31, 26, 19, 15 e 9 a cada 100 compradores).
- **Gerador:** `python3 tools/v6/livro.py`, com texto em `conteudo-v6/` e estilo em `tools/v6/livro.css`. O motor (navegação, celular, PDF, revisão, checklist e teste) continua em `tools/deck/`.

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
