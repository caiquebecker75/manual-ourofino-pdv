"""Lista de imagens geradas no ChatGPT para a v3 do guia.
Rodar: python3 tools/imagens_ia.py [grupo ...] [--paralelo 3]   (grupos: pets, personagem, loja; padrão: todos)"""
import sys, subprocess, concurrent.futures as cf
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
P = "assets/produtos/raw/"; R = "assets/render/"; LOGO = "assets/marca/ourofino_positivo.png"

# ---------------------------------------------------------------- fotos de shooting de animais
PETS = [
    ("pet-capa", "Um golden retriever adulto deitado de frente e um gato tigrado cinza encostando a cabeça no queixo dele, de olhos fechados, num gesto de carinho. O cão olha para a câmera, tranquilo. Enquadramento de meio corpo dos dois."),
    ("pet-00", "Um filhote de beagle sentado, com a cabeça inclinada para o lado, olhar curioso direto para a câmera, orelhas caídas macias."),
    ("pet-01", "Um border collie preto e branco em pé, alerta e animado, segurando na boca uma guia de passeio vermelha lisa, sem marca."),
    ("pet-02", "Um gato laranja tigrado espiando por cima de uma superfície branca: aparecem só a cabeça e as duas patas da frente apoiadas na borda, olhos arregalados de curiosidade."),
    ("pet-03", "Um dachshund de pelo curto marrom avermelhado correndo em direção à câmera, orelhas balançando no ar, boca aberta e alegre. Foto congelada com flash de estúdio, nitidez total."),
    ("pet-04", "Um shih tzu branco e caramelo e um vira-lata caramelo brasileiro de porte médio sentados lado a lado, olhando um para o outro com cumplicidade."),
    ("pet-05", "Um gato frajola preto e branco sentado com postura elegante, cauda em volta das patas, olhar direto e sereno para a câmera."),
    ("pet-06", "Um labrador chocolate deitado de barriga para baixo, cabeça apoiada nas patas da frente, olhando para cima para a câmera com olhar doce."),
    ("pet-07", "Um lulu da pomerânia laranja, pelo volumoso e bem escovado, sorrindo de boca aberta, sentado."),
    ("pet-08", "Um buldogue francês tigrado com a cabeça inclinada e orelhas em pé, expressão atenta e engraçada."),
    ("pet-09", "Um pug bege e um gato branco de olhos azuis sentados lado a lado, encostados de leve um no outro, os dois olhando para a câmera."),
    ("pet-10", "Um vira-lata caramelo brasileiro adulto, porte médio, sentado e olhando para a câmera com a língua levemente para fora, expressão feliz e confiante."),
    ("pet-11", "Um filhote de golden retriever sentado levantando uma pata da frente, como quem dá a pata, olhar alegre."),
    ("pet-12", "Um gato siamês sentado com postura ereta e elegante, olhos azuis, expressão calma."),
    ("pet-fim", "Um vira-lata preto de porte médio e um gato tigrado laranja dormindo juntos, encolhidos lado a lado sobre uma manta cinza clara."),
    ("pet-teste", "Um jack russell terrier pulando no ar, as quatro patas fora do chão, orelhas para cima, expressão de alegria, congelado com flash de estúdio."),
]

# ---------------------------------------------------------------- personagem (promotora ilustrada)
BASE = ("Personagem: Bia, promotora de trade marketing brasileira de uns 28 anos, pele morena, cabelo cacheado castanho preso num rabo de cavalo alto, "
        "sorriso aberto e simpático. Usa camisa polo verde (#10AD31) lisa, sem logotipo, calça jeans azul escura, tênis brancos, "
        "relógio no pulso e um crachá azul-marinho pendurado no pescoço, sem texto.")
PERSONAGEM = [
    ("bia-acena", f"{BASE} Pose: de pé, acenando com a mão direita levantada, como quem dá boas-vindas.", None),
    ("bia-aponta", f"{BASE} Pose: de pé, apontando com o indicador da mão direita para o lado direito do quadro, explicando algo, sorrindo.", "bia-acena"),
    ("bia-joinha", f"{BASE} Pose: de pé, fazendo sinal de positivo com o polegar da mão direita, piscando um olho.", "bia-acena"),
    ("bia-pensa", f"{BASE} Pose: de pé, com a mão no queixo, olhando para cima pensativa, expressão de quem está pensando na resposta.", "bia-acena"),
    ("bia-tablet", f"{BASE} Pose: de pé, segurando um tablet com as duas mãos e olhando para a tela, concentrada.", "bia-acena"),
    ("bia-caixa", f"{BASE} Pose: de pé, segurando nos braços uma caixa de papelão aberta com embalagens coloridas genéricas dentro, sem texto.", "bia-acena"),
    ("bia-explica", f"{BASE} Pose: de pé, com os dois braços abertos e as palmas para cima, explicando com entusiasmo.", "bia-acena"),
    ("bia-atencao", f"{BASE} Pose: de pé, com a palma da mão esquerda estendida para a frente como sinal de atenção, expressão séria mas gentil.", "bia-acena"),
]

# ---------------------------------------------------------------- cenas ilustradas com a personagem
CENA = ("Ilustração em 3D estilizado no padrão de animação de longa-metragem, com cenário de petshop brasileiro limpo e claro "
        "(prateleiras com embalagens coloridas genéricas sem texto legível, piso claro, luz suave). A promotora é EXATAMENTE a personagem da imagem de referência "
        "(rosto, cabelo cacheado no rabo de cavalo, polo verde lisa, crachá azul-marinho, jeans, tênis brancos). Mãos com cinco dedos. Sem texto, sem logotipo inventado. ")
CENAS = [
    ("cena-chegada", CENA + "Cena: a promotora chega ao balcão do petshop e se apresenta, sorrindo e estendendo a mão para cumprimentar um balconista de uns 40 anos, de camiseta cinza e avental azul, atrás do balcão."),
    ("cena-gondola", CENA + "Cena: a promotora agachada em frente à prateleira, puxando para a frente as caixas que vencem primeiro e colocando as novas atrás, concentrada."),
    ("cena-conversa", CENA + "Cena: a promotora mostra algo no tablet para a gerente da loja, uma mulher de uns 45 anos de camisa social azul-clara, as duas em pé conversando ao lado da gôndola."),
    ("cena-tutor", CENA + "Cena: um tutor de uns 35 anos, de camiseta e boné, com um cachorro vira-lata caramelo na guia, olhando a prateleira de produtos para pets enquanto a promotora, ao fundo, arruma a gôndola."),
]

# ---------------------------------------------------------------- cenas de loja (refeitas a partir do esboço 3D, com embalagens reais)
REFS_FARM = [P + "wellpet_a.png", P + "topdog_a.png", P + "leevre_a.png", P + "banni3_a.png"]
LOJA = [
    ("loja-depois", "F-DEPOIS", "retrato", REFS_FARM, "Prateleira da farmácia de um petshop bem organizada: produtos blocados por linha, de frente, etiquetas de preço alinhadas, nenhum buraco."),
    ("loja-antes", "F-ANTES", "retrato", REFS_FARM, "A mesma prateleira desorganizada: buracos de produto em falta, caixas caídas e viradas, sem etiqueta de preço em parte dos produtos, marcas misturadas."),
    ("loja-zonas", "F-GONDOLA-ZONAS", "retrato", REFS_FARM, "Prateleira da farmácia com três faixas coloridas translúcidas marcando as alturas (pés, mãos e olhos) e um boneco de escala neutro ao lado, como foto didática de treinamento. Mantenha as faixas coloridas exatamente como no esboço."),
    ("loja-prateleira-ideal", "F-PRATELEIRA-IDEAL", "quadrada", REFS_FARM, "Farmácia de petshop vista de frente, com cada categoria no lugar: antiparasitários na altura dos olhos ao lado da marca concorrente, vermífugos, suplementos em potes. Testeira azul-marinho no topo com o logotipo Ourofino."),
    ("loja-ponto-extra-certo", "F-PONTO-EXTRA-CERTO", "paisagem", [P + "herbalvet_a.png", LOGO], "Gôndola de higiene do ambiente cheia e, ao lado, um display de chão verde do desinfetante Herbalvet T.A. abastecido com os frascos reais."),
    ("loja-ponto-extra-errado", "F-PONTO-EXTRA-ERRADO", "paisagem", [P + "herbalvet_a.png", LOGO], "A mesma cena, mas a gôndola de higiene ficou com um buraco vazio onde estavam os frascos de Herbalvet T.A., e o display de chão está cheio."),
    ("loja-wobbler", "F-MAT-WOBBLER", "paisagem", [P + "wellpet_a.png", P + "leevre_a.png", LOGO], "Close de um wobbler redondo do WellPET preso na prateleira da farmácia, na altura dos olhos, ao lado das caixas de WellPET e Leevre."),
    ("loja-stopper", "F-MAT-STOPPER", "paisagem", [P + "enziclim_a.png", LOGO], "Stopper verde do EnziClim preso perpendicular à prateleira de higiene do ambiente, ao lado dos frascos borrifadores."),
    ("loja-testeira", "F-MAT-TESTEIRA", "paisagem", REFS_FARM + [LOGO], "Farmácia atrás do balcão com a testeira azul-marinho e faixa verde no topo da prateleira, com o logotipo Ourofino."),
    ("loja-regua", "F-MAT-REGUA", "paisagem", [P + "wellpet_a.png", P + "banni3_a.png", P + "leevre_a.png"], "Close da régua de gôndola verde na borda da prateleira da farmácia, entre as caixas de Banni 3 em cima e WellPET e Leevre embaixo."),
    ("loja-display-balcao", "F-MAT-DISPLAY-BALCAO", "paisagem", [P + "topdog_a.png", LOGO], "Display de balcão rosa do vermífugo Top Dog com as caixas reais dentro, sobre o balcão de atendimento, perto do caixa."),
    ("loja-takeone", "F-MAT-TAKEONE", "paisagem", [LOGO], "Take one de acrílico com folhetos do calendário de vermifugação sobre o balcão, ao lado de uma planta."),
    ("loja-display-chao", "F-MAT-DISPLAY-CHAO", "retrato", [P + "herbalvet_a.png", LOGO], "Display de chão verde do Herbalvet T.A. abastecido, ao lado da gôndola de higiene do ambiente."),
    ("loja-ilha", "F-MAT-ILHA", "paisagem", [P + "herbalvet_a.png", P + "enziclim_a.png", LOGO], "Ilha baixa no corredor com frascos de Herbalvet T.A. e EnziClim, painéis verdes de higiene do ambiente."),
    ("loja-clipstrip", "F-MAT-CLIPSTRIP", "retrato", [P + "banni3_a.png", LOGO], "Clip strip vertical pendurado na lateral da prateleira da farmácia com sachês de Banni 3."),
    ("loja-cartaz", "F-MAT-CARTAZ", "retrato", [P + "leevre_a.png", LOGO], "Cartaz de parede azul-marinho com a coleira Leevre, na área de espera do petshop, ao lado de um banco de madeira e uma planta."),
    ("loja-adesivo", "F-MAT-ADESIVO-CHAO", "paisagem", [LOGO], "Adesivo de chão redondo verde com uma seta, no piso de porcelanato do corredor, indicando o caminho até a farmácia."),
    ("loja-cross", "F-CROSS-MERCH", "paisagem", [P + "wellpet_a.png", LOGO], "Gôndola de ração de cão com sacos de ração sem marca e um wobbler redondo do WellPET preso na prateleira de cima."),
    ("loja-carnaval", "F-ERRO-CARNAVAL", "paisagem", [P + "wellpet_a.png", P + "herbalvet_a.png", LOGO], "Ilha baixa errada: painéis com a arte do WellPET mas cheia de frascos de Herbalvet T.A., sem nenhuma caixa de WellPET. Uma mistura que confunde o cliente."),
    ("loja-capa", "F-CAPA", "paisagem", REFS_FARM + [P + "herbalvet_a.png", LOGO], "Petshop moderno com a farmácia organizada atrás do balcão e um display de Herbalvet T.A. em primeiro plano."),
    ("loja-geral", "F-LOJA", "paisagem", [P + "herbalvet_a.png", LOGO], "Vista geral de um petshop: gôndola de ração, higiene do ambiente, ilha, adesivo de chão e a farmácia atrás do balcão."),
]


def tarefas(grupos):
    t = []
    if "pets" in grupos:
        for nome, desc in PETS: t.append((nome, "pet", "paisagem", [], desc + " Enquadramento com o animal no centro e respiro em volta."))
    if "personagem" in grupos:
        for nome, desc, ref in PERSONAGEM:
            refs = [str(RAIZ / "assets/ia" / f"{ref}.png")] if ref else []
            extra = " Mantenha exatamente o mesmo personagem da imagem de referência (rosto, cabelo, roupa, proporções e estilo de renderização), mudando só a pose." if ref else ""
            t.append((nome, "ilustracao", "retrato", refs, desc + extra))
    if "cenas" in grupos:
        for nome, desc in CENAS: t.append((nome, "ilustracao", "paisagem", [str(RAIZ / "assets/ia/bia-acena.png")], desc))
    if "loja" in grupos:
        for nome, base, prop, refs, desc in LOJA: t.append((nome, "refoto", prop, [R + base + ".png"] + refs, desc))
    return t


def rodar(tf):
    nome, modo, prop, refs, prompt = tf
    if (RAIZ / "assets/ia" / f"{nome}.png").exists(): return nome, "já existe"
    cmd = [sys.executable, str(RAIZ / "tools/chatgpt_img.py"), nome, "--modo", modo, "--proporcao", prop, "--prompt", prompt]
    for r in refs: cmd += ["--ref", r]
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=RAIZ)
    return nome, (p.stdout.strip() or p.stderr.strip()[-300:])


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    par = int(sys.argv[sys.argv.index("--paralelo") + 1]) if "--paralelo" in sys.argv else 3
    grupos = [a for a in args if a in ("pets", "personagem", "cenas", "loja")] or ["pets", "personagem", "cenas", "loja"]
    ts = tarefas(grupos)
    if "personagem" in grupos:  # a base sai primeiro: as outras poses usam ela de referência
        base = [x for x in ts if x[0] == "bia-acena"]; ts = [x for x in ts if x[0] != "bia-acena"]
        if base: print(*rodar(base[0]), flush=True)
    with cf.ThreadPoolExecutor(par) as ex:
        for nome, res in ex.map(rodar, ts): print(nome, res, flush=True)
