# Guia de Execução no PDV · Ourofino Pet

Guia interativo de execução no ponto de venda para promotores, vendedores do distribuidor e equipes de loja. *Tá bem cuidado.*

**Link ao vivo:** https://projetos.75lab.com.br/manual-ourofino-pdv/

Abre no celular e no computador. O botão **PDF** gera a versão impressa em A4 paisagem. O botão **Revisão** mostra as notas que aguardam validação da Ourofino.

## O que tem dentro (versão 6, 49 páginas diagramadas como livro)

- Abertura com a Serafina, a promotora ilustrada que acompanha o guia, e sumário com as páginas.
- Nove capítulos, cada um com capa própria: contato no PDV, trade marketing, básico da gôndola, materiais de PDV, cross, ponto natural e ponto extra, relacionamento e postura, CBV e produtos heróis, prateleira ideal.
- Galeria dos 11 materiais de PDV, os sete produtos heróis com a frase de balcão, comparadores de antes e depois e diagramas da operação.
- Checklist da visita que fica salvo no celular e teste final com nove situações de loja, uma pergunta por vez.
- Ensaio fotográfico próprio de cães e gatos nas cores da Ourofino, fotos de loja com as embalagens reais e ícones animados.
- Cada página tem composição própria, com cabeço, fólio, legendas e notas de fonte, como num livro.

## Como editar

O texto fica em `conteudo-v6/capNN.md` (o `@layout` de cada bloco escolhe a composição da página), um bloco `===` por slide (tipos de slide em `conteudo-v4/_ESPEC.md`, mais `galeria`, `produtos`, `checklist`, `quiz` e `contracapa` da v5). Depois de editar:

```bash
python3 tools/v6/livro.py
```

O comando gera o `index.html`. Não edite o `index.html` à mão.

- Motor de slides: `tools/deck/` (estrutura.css, visual.css, deck.js, icones.py) · diagramas: `tools/diagramas.py`
- Fotos do ensaio: `python3 tools/v6/ensaio.py` gera no ChatGPT (Codex) as que faltam em `assets/ia/`; o `livro.py` converte para `assets/img/v6/`

## Versões anteriores

Ficam congeladas em `versoes/`, com o histórico em `versoes/CHANGELOG.md`.

---

Identidade visual Ourofino Saúde Animal · desenvolvido por **75 LAB**.
