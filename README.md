# Guia de Execução no PDV · Ourofino Pet

Guia interativo de execução no ponto de venda para promotores, vendedores do distribuidor e equipes de loja. *Tá bem cuidado.*

**Link ao vivo:** https://projetos.75lab.com.br/manual-ourofino-pdv/

Abre no celular e no computador. O botão **PDF** gera a versão impressa em A4 paisagem. O botão **Revisão** mostra as notas que aguardam validação da Ourofino.

## O que tem dentro (versão 4, em slides)

- 13 capítulos em seis partes: entender o trade e a loja, a visita, a gôndola, materiais e cross, produtos e postura.
- Glossário A a Z com busca, checklist da visita que fica salvo no celular e teste final com dez situações de loja.
- Fotos de shooting de cães e gatos nas aberturas, uma promotora ilustrada que dá as dicas e fotos de loja com as embalagens reais, feitas no ChatGPT.
- Comparadores de antes e depois, marcações nas fotos e diagramas da operação.
- Fichas dos sete produtos heróis com CBV, ponto natural, cross e material indicado.

## Como editar

O texto fica em `conteudo-v4/capNN.md`, um bloco `===` por slide (formato em `conteudo-v4/_ESPEC.md`). Depois de editar:

```bash
python3 tools/deck/build_deck.py
```

O comando gera o `index.html`. Não edite o `index.html` à mão.

- Motor de slides: `tools/deck/` (estrutura.css, visual.css, deck.js, icones.py) · diagramas: `tools/diagramas.py`
- Cenas 3D: `tools/render/loja2.py` (Blender 5) → `python3 tools/pos.py --todos` gera as imagens em `assets/img/`

## Versões anteriores

Ficam congeladas em `versoes/`, com o histórico em `versoes/CHANGELOG.md`.

---

Identidade visual Ourofino Saúde Animal · desenvolvido por **75 LAB**.
