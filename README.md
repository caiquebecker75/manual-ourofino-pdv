# Guia de Execução no PDV · Ourofino Pet

Guia interativo de execução no ponto de venda para promotores, vendedores do distribuidor e equipes de loja. *Tá bem cuidado.*

**Link ao vivo:** https://caiquebecker75.github.io/manual-ourofino-pdv/

Abre no celular e no computador. O botão **PDF** gera a versão impressa em A4 paisagem. O botão **Revisão** mostra as notas que aguardam validação da Ourofino.

## O que tem dentro (versão 2)

- 13 capítulos em seis partes: entender o trade e a loja, a visita, a gôndola, materiais e cross, produtos e postura.
- Glossário A a Z com busca, checklist da visita que fica salvo no celular e teste final com dez situações de loja.
- Loja 3D fotorrealista com cada material de PDV instalado no lugar certo, comparadores de antes e depois e diagramas da operação.
- Fichas dos sete produtos heróis com CBV, ponto natural, cross e material indicado.

## Como editar

O texto fica em `conteudo/capNN.md` (formato em `conteudo/_ESPEC.md`). Depois de editar:

```bash
python3 tools/build.py
```

O comando gera o `index.html`. Não edite o `index.html` à mão.

- Estilo: `tools/guia.css` · interações: `tools/guia.js` · diagramas: `tools/diagramas.py`
- Cenas 3D: `tools/render/loja2.py` (Blender 5) → `python3 tools/pos.py --todos` gera as imagens em `assets/img/`

## Versões anteriores

Ficam congeladas em `versoes/`, com o histórico em `versoes/CHANGELOG.md`.

---

Identidade visual Ourofino Saúde Animal · desenvolvido por **75 LAB**.
