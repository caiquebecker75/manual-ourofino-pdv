#!/usr/bin/env python3
"""Gera imagem no ChatGPT (gerador da OpenAI) pelo Codex do app ChatGPT do Mac, logado na conta do Caique.
Baseado em ~/abccom-agente/gerador/ia_imagem.py.

Uso: python3 tools/chatgpt_img.py NOME --modo foto|pet|ilustracao|refoto --proporcao paisagem|retrato|quadrada
          [--ref arquivo ...] [--prompt "texto" | --prompt-arq arquivo.txt]
Saída: assets/ia/NOME.png (cache por hash em assets/ia/cache; rodar de novo não gasta geração)."""
import argparse, hashlib, json, shutil, subprocess, sys, time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
IA = RAIZ / "assets" / "ia"; CACHE = IA / "cache"; LOG = IA / "log.jsonl"
CODEX = "/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex"
TAM = {"retrato": ("1024x1536", "retrato vertical 2:3"), "paisagem": ("1536x1024", "paisagem horizontal 3:2"), "quadrada": ("1024x1024", "quadrada 1:1")}

REGRAS = {
    "pet": ("Fotografia de estúdio profissional de animal de estimação, como um shooting publicitário de marca de saúde animal: "
            "câmera full frame, lente 85 mm, f/4, luz de estúdio suave com rebatedor e luz de recorte que separa o pelo do fundo, "
            "pelo com textura e fios individuais nítidos, olhos vivos com reflexo da luz, nariz úmido, expressão natural e carismática. "
            "Fundo branco infinito liso e limpo (#FFFFFF), sem sombra pesada, para recorte. Sem coleira com marca, sem roupa, sem acessório. "
            "Animal anatomicamente perfeito (quatro patas, número certo de dedos, orelhas e olhos simétricos). "
            "Nada de aparência de ilustração, 3D ou IA. Sem texto, sem marca d'água."),
    "editorial": ("Fotografia editorial de animal de estimação para um livro impresso de marca de saúde animal, no padrão de revista de design: "
                  "câmera de médio formato, lente 80 mm, f/5.6, uma luz grande e suave de janela vinda de um lado, sombra de contato natural no chão, "
                  "pelo com textura e fios individuais nítidos, olhos vivos com reflexo da luz, expressão natural e calma, leve grão de filme, cor fiel. "
                  "Animal anatomicamente perfeito (quatro patas, dedos certos, orelhas e olhos simétricos), sem coleira com marca, sem roupa. "
                  "Nada de aparência de ilustração, 3D, render ou imagem de IA; nada de pele plastificada nem brilho exagerado. "
                  "Sem texto, sem logotipo, sem marca d'água."),
    "foto": ("Fotografia realista de verdade feita por fotógrafo de varejo: luz, sombra, reflexo e textura físicas, lente de câmera profissional, "
             "nada de aparência de render 3D, ilustração ou imagem de IA. Mantenha EXATAMENTE a forma, as cores e os logotipos das embalagens "
             "e peças das imagens de referência. Não escreva nenhum texto novo: se um texto não puder sair perfeito, deixe a área lisa em vez de inventar letras. "
             "Sem marca d'água."),
    "refoto": ("A primeira imagem anexada é um esboço 3D da cena. Refaça como FOTOGRAFIA REAL de um petshop brasileiro: mesma composição, "
               "mesmo enquadramento, mesmos móveis e a mesma posição de cada produto e peça, mas com materiais, luz e imperfeições do mundo real "
               "(reflexo no piso, poeira mínima, sombras de contato, variação de iluminação, profundidade de campo de câmera full frame). "
               "As demais imagens anexadas são as embalagens e o logotipo reais: mantenha EXATAMENTE as cores, o logotipo e a arte delas. "
               "Não invente texto novo; se um texto não puder sair perfeito, deixe a área lisa. Nada de aparência de render, ilustração ou IA. Sem marca d'água."),
    "ilustracao": ("Ilustração de personagem em 3D estilizado, no padrão de animação de longa-metragem (proporções levemente cartunescas, "
                   "cabeça um pouco maior, olhos expressivos, pele com subsurface scattering, tecido com textura), renderização limpa e profissional. "
                   "Se for personagem sozinho: corpo inteiro, de frente ou três quartos, fundo branco liso (#FFFFFF) sem cenário e sem sombra no chão, para recorte. "
                   "Mãos com cinco dedos corretos. Sem texto, sem logotipo inventado, sem marca d'água."),
}


def chave(nome, prompt, refs, prop, modo):
    h = hashlib.sha256((nome + prompt + prop + modo + REGRAS[modo]).encode())
    for r in refs: h.update(Path(r).read_bytes())
    return h.hexdigest()[:16]


def png(r):
    r = Path(r).resolve()
    if r.suffix.lower() in (".png", ".jpg", ".jpeg"): return str(r)
    from PIL import Image
    alvo = CACHE / "refs" / (r.stem + ".png"); alvo.parent.mkdir(parents=True, exist_ok=True)
    if not alvo.exists(): Image.open(r).convert("RGBA").save(alvo)
    return str(alvo)


def registrar(**k):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as f: f.write(json.dumps({"em": time.strftime("%Y-%m-%dT%H:%M:%S"), **k}, ensure_ascii=False) + "\n")


def gerar(nome, prompt, modo="pet", prop="paisagem", refs=(), tentativas=2, tempo=600):
    refs = [png(r) for r in refs]
    k = chave(nome, prompt, refs, prop, modo)
    pronto = CACHE / f"{k}.png"; final = IA / f"{nome}.png"
    CACHE.mkdir(parents=True, exist_ok=True)
    if not pronto.exists():
        tam, desc = TAM[prop]
        pasta = CACHE / f"_trab-{k}"; pasta.mkdir(exist_ok=True)
        pedido = (f"Use a ferramenta de geração de imagem e gere UMA imagem no tamanho {tam} ({desc}), na melhor qualidade disponível.\n\n"
                  f"{prompt}\n\n{REGRAS[modo]}\n\nSalve o arquivo final nesta pasta com o nome saida.png e responda apenas o caminho do arquivo.")
        erro = ""
        for n in range(1, tentativas + 1):
            t0 = time.time(); cmd = [CODEX, "exec", "--skip-git-repo-check", "-s", "workspace-write"]
            for r in refs: cmd += ["-i", r]
            try:
                p = subprocess.run(cmd, input=pedido, text=True, capture_output=True, cwd=pasta, timeout=tempo)
                log = (p.stdout + p.stderr)[-1500:]
            except subprocess.TimeoutExpired:
                log = "tempo esgotado"
            arq = pasta / "saida.png"
            if "out of credits" in log or "usage limit" in log.lower() or "usage_limit" in log:
                registrar(nome=nome, ok=False, erro="SEM COTA", log=log[-300:]); shutil.rmtree(pasta, ignore_errors=True)
                print("SEM COTA:", log[-300:], file=sys.stderr); sys.exit(3)
            if arq.exists():
                registrar(nome=nome, tentativa=n, ok=True, segundos=round(time.time() - t0)); shutil.move(str(arq), pronto); break
            erro = log; registrar(nome=nome, tentativa=n, ok=False, erro=log[-400:])
        shutil.rmtree(pasta, ignore_errors=True)
        if not pronto.exists(): raise RuntimeError(f"ChatGPT não gerou {nome}: {erro[-400:]}")
    IA.mkdir(parents=True, exist_ok=True); shutil.copy2(pronto, final)
    return str(final)


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("nome"); a.add_argument("--modo", default="pet", choices=list(REGRAS))
    a.add_argument("--proporcao", default="paisagem", choices=list(TAM)); a.add_argument("--ref", action="append", default=[])
    a.add_argument("--prompt", default=""); a.add_argument("--prompt-arq")
    x = a.parse_args()
    pr = Path(x.prompt_arq).read_text() if x.prompt_arq else x.prompt
    print(gerar(x.nome, pr, x.modo, x.proporcao, x.ref))
