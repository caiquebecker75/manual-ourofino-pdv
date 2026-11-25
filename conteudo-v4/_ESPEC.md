# Especificação de conteúdo · Guia Ourofino Pet v4 (formato slide)

Cada capítulo é um arquivo `capNN.md`. O build transforma cada bloco `===` em um slide 16:9 (computador) e em uma tela vertical (celular). A v3 em `../conteudo/` é a base de conteúdo; a v4 reescreve tudo em slides, mais explicativo e mais profundo.

## 1. O que mudou do texto da v3 (pedido do cliente em 24/11)
- O texto estava **difícil de entender e raso ao mesmo tempo**. Agora cada conceito vem explicado por inteiro: o que é, por que importa (com a consequência concreta na loja, de preferência com um número de fonte confiável), como fazer, e um exemplo de loja pet.
- Um assunto por slide. Nada de frase telegráfica que pressupõe conhecimento. Nada de enrolação.
- Linguagem de conversa com o promotor: "você". Frases de até 20 palavras. Parágrafos de 1 a 3 frases.
- Profundidade de quem trabalha com trade há anos: mecanismo por trás de cada regra (por que o olho do tutor vai para a faixa entre 1,20 e 1,60 m, por que ruptura faz perder o cliente e não só a venda do dia, o que é giro e como ele aparece no pedido do distribuidor).
- Personagem: **Serafina**, promotora experiente da Ourofino. Fala em 1ª pessoa nos slides `serafina`, com tom de colega que já passou por aquilo. Nunca fala "como IA", nunca faz piada forçada.

## 2. Proibido (continua valendo)
- Travessão (— ou –). Advérbios vazios (realmente, simplesmente, basicamente, extremamente...). "Não é X, é Y". Frases de efeito. Perguntas retóricas respondidas na hora. Trincas forçadas. Emojis. "Jornada", "ecossistema", "potencializar", "alavancar", "insight", "sinergia".
- Conteúdo vetado pela cliente: negociação (espaço, ponta, desconto, bonificação), produto âncora, e-commerce, incentivo/comissão, papéis e responsabilidades / "faço, apoio, escalo", classificação de material em estímulo/atração/conversão, prescrição ou dose, falar mal ou nomear concorrente, linguagem de farmácia humana ou cosmético humano, nomes internos (Elanco, Facto, BRF, ProTrade) e nomes de pessoas da reunião.
- Dados com número só com fonte confiável e verificável (estudo, associação, instituto). Coloque a fonte no slide (`@fonte`). Sem fonte, sem número.

## 3. Cabeçalho do capítulo
```
---
cap: 5
parte: Na gôndola
titulo: O básico da gôndola
manuscrito: na gôndola
abertura: Uma ou duas frases que abrem o capítulo na capa.
objetivo:
  - O que a pessoa vai saber fazer no fim (2 a 4 itens)
publico: Promotor, vendedor do distribuidor e balconista
tempo: 12 min
---
```

## 4. Tipos de slide (cada bloco começa com `=== tipo | título` e vai até o próximo `===`)

| tipo | para quê | limite de texto |
|---|---|---|
| `conceito` | explicar uma ideia | até 110 palavras + `@na-pratica` de até 40 |
| `passos` | sequência de ação | 3 a 6 passos, cada um `N. **Título** · explicação de até 25 palavras` |
| `termo` | definir uma palavra do trade | definição até 45 palavras + `@exemplo` até 35 |
| `porque` | o mecanismo/consequência por trás de uma regra, com dado e fonte | até 90 palavras + `@dado` + `@fonte` |
| `comparar` | certo x errado | `+ certo` e `- errado`, 2 a 4 de cada, até 18 palavras cada |
| `erro` | erro comum de campo | `**O que acontece:** ...` e `**Faça assim:** ...`, até 45 palavras cada |
| `serafina` | fala da personagem | até 50 palavras; opcional `@pose aponta|explica|joinha|acena|pensa|tablet|caixa|atencao` |
| `figura` | imagem grande com explicação | `@fig ID` + texto até 60 palavras |
| `cards` | 3 a 6 itens lado a lado | `**Título** · texto até 25 palavras` |
| `tabela` | comparação em colunas | tabela markdown, até 5 linhas x 4 colunas |
| `conversa` | fala pronta | `quem: "fala"` (2 a 6 falas) |
| `teste` | pergunta de situação | `? pergunta`, `- [ ]`/`- [x]` (3 opções), `> explicação` até 35 palavras |
| `resumo` | fechamento do capítulo | 3 a 5 itens de até 15 palavras |
| `validar` | nota para a Ourofino (só no modo revisão; não vira slide sozinho, anexa ao slide anterior) | livre |

Marcadores que podem ir dentro de qualquer slide: `@icone nome` (ícone animado; ver lista), `@fig ID`, `@na-pratica`, `@exemplo`, `@dado`, `@fonte`, `@pose`.

Ícones disponíveis: loja, caminhao, fabrica, pata, vet, relogio, calendario, checklist, camera, prateleira, caixa, etiqueta, olho, alvo, balao, conversa, lampada, alerta, certo, errado, tablet, wobbler, display, ilha, seta-chao, cartaz, carrinho, escudo, comprimido, frasco, casa, pessoa, pessoas, grafico, mapa, lupa, estrela, coracao, cao, gato, seta, mao, folha, moeda, pin.

Figuras disponíveis: as da v3 (F-ANTES, F-DEPOIS, F-GONDOLA-ZONAS, F-PRATELEIRA-IDEAL, F-PONTO-EXTRA-CERTO, F-PONTO-EXTRA-ERRADO, F-MAT-WOBBLER, F-MAT-STOPPER, F-MAT-TESTEIRA, F-MAT-REGUA, F-MAT-DISPLAY-BALCAO, F-MAT-TAKEONE, F-MAT-DISPLAY-CHAO, F-MAT-ILHA, F-MAT-CLIPSTRIP, F-MAT-CARTAZ, F-MAT-ADESIVO-CHAO, F-CROSS-MERCH, F-ERRO-CARNAVAL), diagramas D-CAMINHO-PRODUTO, D-MAPA-LOJA, D-QUEM-DECIDE, D-VISITA, D-FIFO, D-BLOCAGEM, D-CROSS-MAPA, D-CBV, e as embalagens P-WELLPET, P-BANNI3, P-TOPDOG, P-LEEVRE, P-HERBALVET, P-ENZICLIM, P-PLENIPIL.

## 5. Ritmo de um capítulo (12 a 22 slides)
capa (automática) → 1 slide `serafina` abrindo o assunto → blocos de `conceito`/`porque`/`termo` intercalados com `figura`, `passos`, `comparar` e `erro` → 1 ou 2 `teste` → `resumo`.
Nunca dois slides de texto puro seguidos: depois de um `conceito`, venha algo visual (`figura`, `cards`, `passos` com ícones, `comparar`).

## 6. Mapa de capítulos da v4 (ordem do guia da Elanco + pedidos da reunião de 19/11)

| arquivo | capítulo | o que cobre | base na v3 |
|---|---|---|---|
| cap00.md | Prazer, Serafina | a personagem se apresenta: quem ela é (promotora da Ourofino há anos, já errou e aprendeu), o que vai acompanhar no guia, como ela vai aparecer (dicas, alertas, testes), convite para começar. 6 a 8 slides, quase todos `serafina` | novo |
| cap01.md | Objetivo do guia | para que serve, quem usa, como usar no celular, no treinamento e no PDF, como ler os tipos de slide, o que o guia não cobre (negociação, preço, e-commerce) | cap00 |
| cap02.md | Contato no PDV: antes, durante e depois | pré-visita (objetivo, histórico, pendências, material, rota), visita (8 passos na ordem), pós-visita (registro, fotos, avisar supervisor, próxima visita) | cap03 |
| cap03.md | O que é trade marketing | trade em uma frase; mito "é só promotora sexta e sábado"; caminho do produto; sell-in e sell-out; canais e ciclo de vendas (leve); o papel de quem está na loja; por que a decisão acontece na loja (dado com fonte) | cap01 |
| cap04.md | O básico da gôndola | ponto natural; disponível, limpo, com preço, na validade; ruptura e o que ela custa (dado com fonte); FIFO; frente (facing); blocagem; zonas de altura; ao lado da concorrente; antes e depois | cap05 |
| cap05.md | Materiais de PDV | para cada material: o que é, para que serve, onde colocar, onde nunca colocar, como instalar, quando tirar (wobbler, stopper, testeira, régua, display de balcão, take one, display de chão, ilha, clip strip, cartaz, adesivo de chão). Sem estímulo/atração/conversão | cap08 |
| cap06.md | Cross merchandising e cross selling | separar os dois; a mecânica para pensar sozinho (o que o tutor está fazendo, do que mais ele vai precisar); pares com os heróis; o erro do carnaval; exercício "onde você colocaria" | cap09 |
| cap07.md | Ponto natural e ponto extra | definições; quando montar ponto extra; a regra de nunca esvaziar o ponto natural; certo e errado | cap06 |
| cap08.md | Relacionamento em loja | você é convidado; fala de chegada palavra por palavra; banheiro, água, onde ficar; como falar sem atrapalhar; pilares (confiança, rapidez de resposta, reconhecimento) com a frase do lojista; separar treinamento de execução; como encerrar. Sem negociação | cap04 |
| cap09.md | Postura em campo | sempre e nunca; celular e fotos; uniforme e crachá; segurança (escada, peso, produto vencido); quando avisar o supervisor | cap12 |
| cap10.md | Conhecendo a loja e quem decide | tipos de loja; mapa e fluxo da loja (o caminho do tutor até o balcão); onde a farmácia fica; quem é quem; quem decide em cada tipo de loja (matriz); balconista x gerente x tutor | cap02 |
| cap11.md | Como falar de produto: CBV | característica, benefício, vantagem; exemplo passo a passo; balconista x gerente; o que pode e o que não pode dizer | cap10 |
| cap12.md | Produtos heróis | por categoria (prevenção e proteção: WellPET, Banni 3, Top Dog, Leevre; desinfecção: Herbalvet T.A., EnziClim; suplementos: Plenipil): ficha de cada herói com CBV, onde fica, cross, material | cap11 |
| cap13.md | Prateleira ideal | visão macro sem planograma; agrupar por necessidade; zona quente e prateleiras de cima; ao lado da concorrente; como adaptar ao espaço real | cap07 |
| cap14.md | Considerações finais | a Serafina fecha: o que levar daqui, o hábito de cada visita, onde buscar ajuda, convite ao checklist e ao teste | novo |
| checklist.md, glossario.md, teste-final.md | apêndices | mesmo formato da v3, revisados | idem |

## 7. A voz da Serafina
Promotora da Ourofino, uns 30 anos, anos de rua, simpática e direta. Fala como colega mais experiente: "Já aconteceu comigo...", "Repara em uma coisa...", "Se eu pudesse te dar um conselho só...". Usa "tá" e "pra" com moderação (tom da marca "Tá bem cuidado"). Nunca infantiliza, nunca faz trocadilho, nunca fala de si como personagem.

## 8. Marcador extra
`@lembre texto` → faixa de fechamento "Lembre-se" no pé do slide (até 25 palavras). Use em 1 de cada 3 ou 4 slides, nunca em dois seguidos.

## 9. Exemplo de slide no nível esperado
```
=== porque | Por que um buraco na prateleira custa mais que uma venda
Quando o tutor não acha o produto que procura, ele não volta outro dia. Ele resolve na hora: leva outra marca, compra em outra loja ou desiste. A venda perdida hoje vira o hábito de comprar o concorrente amanhã.
Por isso a primeira coisa que você confere na gôndola é se o produto está lá. Material bonito ao lado de prateleira vazia não vende nada.
@dado Quando falta o produto, 31% dos compradores vão a outra loja e 26% trocam de marca.
@fonte ECR / Gruen, Corsten e Bharadwaj, "Retail Out-of-Stocks", 2002.
@icone prateleira
@lembre Produto na prateleira vem antes de qualquer material.
```
(o dado acima é um exemplo de formato; confira cada número na fonte antes de usar)
