"""Ensaio fotográfico da v6: pets no mesmo estúdio, fundos nas cores da Ourofino, espaço planejado para o texto.
Roda em sequência pelo Codex (tools/chatgpt_img.py). python3 tools/v6/ensaio.py [nome ...]"""
import subprocess, sys, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHAPA = ("Fundo infinito de papel liso na cor {cor}, parede e chão da mesma cor, sem objetos, sem degradê forte. ")
FOTOS = [
  ("v6-c01", "paisagem", "editorial", CHAPA.format(cor="cinza muito claro e quente (#EFEFEF)") +
   "Um cão vira-lata caramelo brasileiro adulto, de porte médio, sentado e atento, com a cabeça levemente inclinada, olhando para a câmera. O cão fica no terço esquerdo do quadro, inteiro, com sombra suave no chão; os dois terços da direita são só fundo vazio, para texto. Horizontal."),
  ("v6-c02", "paisagem", "editorial", CHAPA.format(cor="verde vivo (#10AD31)") +
   "Um dachshund de pelo curto marrom-avermelhado caminhando de perfil da esquerda para a direita, focinho erguido, uma pata da frente no ar. O cão ocupa o terço inferior direito do quadro, inteiro; a metade de cima e o lado esquerdo ficam vazios, para título. Horizontal."),
  ("v6-c03", "paisagem", "editorial", CHAPA.format(cor="azul médio (#007CC1)") +
   "Um beagle adulto deitado de barriga no chão, queixo apoiado nas patas da frente, olhando para cima e para a esquerda, curioso. O cão fica na metade direita do quadro, perto do chão; a metade esquerda e a parte de cima ficam vazias. Horizontal."),
  ("v6-c04", "paisagem", "editorial", CHAPA.format(cor="ciano claro (#20D5F2)") +
   "Um gato laranja tigrado espiando por cima da borda inferior do quadro: aparecem só a cabeça, as orelhas e as duas patas da frente apoiadas na borda, olhos bem abertos. O gato fica no centro-direita, na parte de baixo; toda a metade de cima fica vazia. Horizontal."),
  ("v6-c05", "paisagem", "editorial", CHAPA.format(cor="branco quente (#F4F4F2)") +
   "Um buldogue francês branco e malhado e um gato frajola (preto e branco) sentados lado a lado no chão, virados um para o outro, como se conversassem. Os dois ficam no terço direito do quadro, inteiros, com sombra suave; o resto do quadro fica vazio. Horizontal."),
  ("v6-c06", "paisagem", "editorial", CHAPA.format(cor="azul-marinho profundo (#072047)") +
   "Um jack russell terrier deitado com o queixo encostado no chão, olhando para a câmera, câmera bem baixa, na altura do chão. O cão fica na faixa de baixo, do centro para a direita; a metade de cima fica vazia. Horizontal."),
  ("v6-c07", "paisagem", "editorial",
   "Um gato cinza de pelo curto (british shorthair) sentado com elegância sobre o balcão de madeira clara de um petshop de bairro brasileiro, ao lado de uma pequena balança antiga. Ao fundo, prateleiras com sacos e caixas de produtos pet bem desfocadas (sem marcas legíveis), luz de janela lateral quente. O gato fica no terço direito; o lado esquerdo do quadro é o fundo desfocado, mais escuro e calmo, para texto. Horizontal."),
  ("v6-c08", "paisagem", "editorial", CHAPA.format(cor="verde vivo (#10AD31)") +
   "Um filhote de labrador cor chocolate sentado, cabeça inclinada, orelhas macias, olhando para a câmera com curiosidade. Fica no centro-direita do quadro, inteiro; o lado esquerdo fica vazio. Horizontal."),
  ("v6-c09", "paisagem", "editorial", CHAPA.format(cor="azul médio (#007CC1)") +
   "Um gato siamês sentado no alto de uma estante branca simples de três prateleiras, vazia, olhando para baixo para a câmera. A estante e o gato ficam no terço direito; o resto do quadro é fundo vazio. Horizontal."),
  ("v6-fim", "paisagem", "editorial", CHAPA.format(cor="azul-marinho profundo (#072047)") +
   "Um filhote de cachorro (vira-lata caramelo e branco) e um filhote de gato tigrado dormindo juntos, enroscados sobre uma manta de tricô cinza-clara. Ficam no terço direito do quadro, perto do chão; o resto do quadro é fundo vazio. Horizontal."),
  ("v6-sumario", "retrato", "editorial", CHAPA.format(cor="branco quente (#F4F4F2)") +
   "Um border collie preto e branco sentado, olhando para cima e para a esquerda, atento, como se esperasse uma instrução. Corpo inteiro, ocupando a metade de baixo do quadro vertical, com sombra suave no chão. Vertical."),
  ("v6-kit", "paisagem", "foto",
   "Foto vista de cima (flat lay) sobre uma mesa cinza-clara: o kit de visita de uma promotora de petshop organizado com espaço entre os itens. Um celular com a tela apagada, um rolo de fita dupla face, uma flanela de microfibra verde dobrada, um bloco de anotações aberto com uma caneta, um crachá com cordão azul-marinho sem texto, um rolo de etiquetas de preço em branco e três caixinhas de medicamento veterinário sem nenhum texto ou marca. Luz de janela suave, sombras curtas. Horizontal."),
  ("v6-celular-gondola", "paisagem", "foto",
   "Por cima do ombro de uma promotora: as mãos dela seguram um celular na horizontal e fotografam uma prateleira de farmácia de petshop arrumada, com caixas coloridas alinhadas e etiquetas de preço amarelas. A tela do celular mostra a mesma prateleira. Caixas sem marcas legíveis. Profundidade de campo rasa, luz de loja. Horizontal."),
  ("v6-maos-prateleira", "paisagem", "foto",
   "Close de duas mãos alinhando caixas de medicamento veterinário numa prateleira branca de loja, deixando todas de frente, em bloco, com etiquetas de preço amarelas embaixo. Caixas em tons de verde, azul e branco, sem nenhum texto legível. Luz de loja suave, profundidade de campo rasa. Horizontal."),
  ("v6-tutor-balcao", "paisagem", "foto",
   "Dentro de um petshop pequeno de bairro brasileiro: uma tutora de uns 40 anos, vista de perfil, com um cão vira-lata preto na guia, conversa com o atendente atrás do balcão. Prateleiras de produtos ao fundo, desfocadas e sem marcas legíveis. Luz natural da porta, clima de dia comum. Pessoas com aparência natural, roupas simples. Horizontal."),
  ("v6-cao-petisco", "paisagem", "editorial",
   "Close de um cão sem raça definida, pelo preto e caramelo, pegando com delicadeza um petisco redondo marrom da palma aberta de uma mão humana, dentro de casa, luz de janela quente, fundo de sala desfocado. Horizontal."),
  ("v6-filhote-tapete", "paisagem", "editorial",
   "Um filhote de cachorro vira-lata branco com manchas caramelo sentado sobre um tapete higiênico branco no chão de madeira clara de um apartamento, olhando para a câmera, luz de janela suave. O filhote fica no terço direito. Horizontal."),
  ("v6-vet-gato", "retrato", "foto",
   "Numa clínica veterinária clara, uma veterinária de jaleco branco segura no colo um gato tigrado calmo, olhando para ele. Enquadramento do peito para cima, rosto dela de três quartos, natural. Fundo da clínica desfocado, luz suave. Vertical."),
  ("v6-cao-passeio", "retrato", "editorial",
   "Um cão de porte médio, pelo dourado, usando uma coleira simples verde sem nenhuma marca, caminhando numa calçada arborizada de bairro brasileiro, câmera baixa na altura do cão, fim de tarde, fundo desfocado. Vertical."),
  ("v6-gato-racao", "paisagem", "editorial",
   "Num corredor de petshop, um gato tigrado cinza cheira com curiosidade uma pilha de sacos de areia sanitária e de ração para gatos no chão. Sacos de cores claras, sem nenhuma marca ou texto legível. Luz de loja suave, profundidade de campo rasa. Horizontal."),
  ("v6-gato-olhar", "retrato", "editorial", CHAPA.format(cor="azul-marinho profundo (#072047)") +
   "Retrato de um gato tigrado cinza e branco sentado, olhando diretamente para a câmera, olhos verdes. Corpo inteiro na metade de baixo do quadro vertical. Vertical."),
]
so = sys.argv[1:]
for nome, prop, modo, pr in FOTOS:
    if so and nome not in so: continue
    if os.path.exists(os.path.join(R, "assets/ia", nome + ".png")): print("já existe", nome); continue
    r = subprocess.run([sys.executable, os.path.join(R, "tools/chatgpt_img.py"), nome, "--modo", modo, "--proporcao", prop, "--prompt", pr], capture_output=True, text=True)
    print(nome, "ok" if r.returncode == 0 else "ERRO " + r.stderr[-300:], flush=True)
    if r.returncode == 3: break
