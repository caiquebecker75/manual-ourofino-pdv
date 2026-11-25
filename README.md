# Guia de Execução no PDV · Ourofino Pet

Guia interativo de execução no ponto de venda para promotores, vendedores do distribuidor e equipes de loja. *Tá bem cuidado.*

**Link ao vivo:** https://projetos.75lab.com.br/manual-ourofino-pdv/

Abre no celular e no computador. O botão **PDF** gera a versão impressa em A4 paisagem. O botão **Revisão** mostra as notas que aguardam validação da Ourofino.

## O que tem dentro (versão 5, 49 slides)

- Abertura com a Serafina, a promotora ilustrada que acompanha o guia, e sumário com as páginas.
- Nove capítulos, cada um com capa própria: contato no PDV, trade marketing, básico da gôndola, materiais de PDV, cross, ponto natural e ponto extra, relacionamento e postura, CBV e produtos heróis, prateleira ideal.
- Galeria dos 11 materiais de PDV, os sete produtos heróis com a frase de balcão, comparadores de antes e depois e diagramas da operação.
- Checklist da visita que fica salvo no celular e teste final com nove situações de loja, uma pergunta por vez.
- Fotos de shooting de cães e gatos, fotos de loja com as embalagens reais e ícones animados.

## Como editar

O texto fica em `conteudo-v5/capNN.md`, um bloco `===` por slide (tipos de slide em `conteudo-v4/_ESPEC.md`, mais `galeria`, `produtos`, `checklist`, `quiz` e `contracapa` da v5). Depois de editar:

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
