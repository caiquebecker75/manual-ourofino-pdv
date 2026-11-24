"""Loja-modelo Ourofino em 3D (Blender 5.x, Cycles).
Uso:
  Blender -b --factory-startup -P tools/render/loja.py -- --root <repo> --shots F-DEPOIS,F-ANTES --samples 160 [--scale 1.0]
Gera assets/render/<SHOT>.png e atualiza assets/render/anot.json com pontos projetados (0-100%) para anotar na página.
"""
import bpy, bmesh, json, math, os, random, sys
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def arg(name, default=None):
    return argv[argv.index(name) + 1] if name in argv else default
ROOT = arg("--root", os.getcwd())
SHOTS = [s for s in arg("--shots", "F-DEPOIS").split(",") if s]
SAMPLES = int(arg("--samples", "160"))
SCALE = float(arg("--scale", "1.0"))
TEX = os.path.join(ROOT, "assets/tex/")
OUT = os.path.join(ROOT, "assets/render/")
os.makedirs(OUT, exist_ok=True)
CAIXAS = json.load(open(TEX + "caixas.json"))

# ----------------------------------------------------------------- base
def reset():
    MATS.clear()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"
    sc.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "METAL"; prefs.get_devices()
    for d in prefs.devices: d.use = d.type == "METAL"
    sc.cycles.device = "GPU"
    sc.cycles.samples = SAMPLES
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 8
    sc.cycles.caustics_reflective = False; sc.cycles.caustics_refractive = False
    sc.render.film_transparent = False
    try:
        sc.view_settings.view_transform = "AgX"
        sc.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass
    sc.view_settings.exposure = -0.35
    w = bpy.data.worlds.new("mundo"); sc.world = w; w.use_nodes = True
    bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.86, 0.87, 0.88, 1); bg.inputs[1].default_value = 0.22
    return sc

def link(ob, col=None):
    (col or bpy.context.scene.collection).objects.link(ob); return ob

MATS = {}
def mat(name, rgb, rough=0.5, metal=0.0, alpha=1.0, emit=0.0, transm=0.0):
    key = (name,)
    if key in MATS: return MATS[key]
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*rgb, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    if transm: p.inputs["Transmission Weight"].default_value = transm
    if emit:
        p.inputs["Emission Color"].default_value = (*rgb, 1); p.inputs["Emission Strength"].default_value = emit
    if alpha < 1: p.inputs["Alpha"].default_value = alpha
    MATS[key] = m; return m

def img(path):
    return bpy.data.images.load(path, check_existing=True)

def mat_img(name, path, coord="UV", proj="FLAT", cut=False, rough=0.42, gloss=False):
    if name in MATS: return MATS[name]
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links
    p = N["Principled BSDF"]; p.inputs["Roughness"].default_value = 0.22 if gloss else rough
    tc = N.new("ShaderNodeTexCoord"); ti = N.new("ShaderNodeTexImage"); ti.image = img(path)
    ti.extension = "CLIP" if proj == "FLAT" else "REPEAT"; ti.projection = proj
    if coord == "FRONT":  # projeta a imagem na face -Y usando coordenadas geradas (X,Z)
        sp = N.new("ShaderNodeSeparateXYZ"); cb = N.new("ShaderNodeCombineXYZ")
        L.new(tc.outputs["Generated"], sp.inputs[0]); L.new(sp.outputs["X"], cb.inputs["X"]); L.new(sp.outputs["Z"], cb.inputs["Y"])
        L.new(cb.outputs[0], ti.inputs["Vector"])
    elif coord == "GEN":
        L.new(tc.outputs["Generated"], ti.inputs["Vector"])
    else:
        L.new(tc.outputs["UV"], ti.inputs["Vector"])
    L.new(ti.outputs["Color"], p.inputs["Base Color"])
    if cut:
        gt = N.new("ShaderNodeMath"); gt.operation = "GREATER_THAN"; gt.inputs[1].default_value = 0.5
        L.new(ti.outputs["Alpha"], gt.inputs[0])
        tr = N.new("ShaderNodeBsdfTransparent"); mx = N.new("ShaderNodeMixShader"); out = N["Material Output"]
        L.new(gt.outputs[0], mx.inputs[0]); L.new(tr.outputs[0], mx.inputs[1]); L.new(p.outputs[0], mx.inputs[2])
        L.new(mx.outputs[0], out.inputs["Surface"])
    MATS[name] = m; return m

# ----------------------------------------------------------------- primitivas
def box(name, w, d, h, loc, mats, rot_z=0.0, bevel=0.0, col=None, front_idx=0):
    """caixa com origem no centro da base. mats = [frente(-Y), lados, topo] (repete se faltar)."""
    me = bpy.data.meshes.new(name); bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co.x *= w; v.co.y *= d; v.co.z = (v.co.z + 0.5) * h
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me)
    for m in mats: me.materials.append(m)
    for pg in me.polygons:
        n = pg.normal
        if n.y < -0.9: pg.material_index = 0
        elif n.z > 0.9 and len(mats) > 2: pg.material_index = 2
        else: pg.material_index = min(1, len(mats) - 1)
    ob.location = loc; ob.rotation_euler = (0, 0, rot_z)
    if bevel:
        b = ob.modifiers.new("bev", "BEVEL"); b.width = bevel; b.segments = 2; b.limit_method = "ANGLE"
    return link(ob, col)

def plane(name, w, h, loc, m, rot=(0, 0, 0), col=None):
    """plano vertical voltado para -Y, origem no centro da base"""
    me = bpy.data.meshes.new(name)
    verts = [(-w / 2, 0, 0), (w / 2, 0, 0), (w / 2, 0, h), (-w / 2, 0, h)]
    me.from_pydata(verts, [], [(0, 1, 2, 3)]); me.update()
    uv = me.uv_layers.new();
    for i, c in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]): uv.data[i].uv = c
    if me.polygons[0].normal.y > 0: me.flip_normals()
    me.materials.append(m)
    ob = bpy.data.objects.new(name, me); ob.location = loc; ob.rotation_euler = rot
    return link(ob, col)

def floor_decal(name, size, loc, m, rot_z=0.0):
    me = bpy.data.meshes.new(name); s = size / 2
    me.from_pydata([(-s, -s, 0), (s, -s, 0), (s, s, 0), (-s, s, 0)], [], [(0, 1, 2, 3)]); me.update()
    uv = me.uv_layers.new()
    for i, c in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]): uv.data[i].uv = c
    me.materials.append(m); ob = bpy.data.objects.new(name, me)
    ob.location = loc; ob.rotation_euler = (0, 0, rot_z); return link(ob)

def cyl(name, r, h, loc, mats, seg=32):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=h)
    for v in bm.verts: v.co.z += h / 2
    bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    for pg in me.polygons: pg.material_index = 1 if abs(pg.normal.z) > 0.9 and len(mats) > 1 else 0
    ob = bpy.data.objects.new(name, me); ob.location = loc
    sm = ob.modifiers.new("s", "BEVEL"); sm.width = 0.003; sm.segments = 2
    return link(ob)

# ----------------------------------------------------------------- produtos
def side_mat(sku):
    c = CAIXAS[sku]["side"]; return mat("lado_" + sku, tuple(c), rough=0.4)

def dims(kind, key):
    if kind == "box": return CAIXAS[key]["dims"]
    if kind == "bb": return {"herbalvet": (0.14, 0.12, 0.27), "enziclim": (0.098, 0.08, 0.25), "plenipil": (0.13, 0.08, 0.12)}[key]
    if kind == "gen": return key[1]
    if kind == "jar": return (key[1] * 2, key[1] * 2, key[2])
    if kind == "bag": return key[1]

def product(kind, key, x, y, z, rz=0.0, tag=None):
    w, d, h = dims(kind, key)
    if kind == "box":
        fm = mat_img("frente_" + key, TEX + key + "_front.png", coord="FRONT", gloss=True)
        lt = CAIXAS[key]["side"]; top = mat("topo_" + key, tuple(min(1, c * 1.08 + 0.05) for c in lt), rough=0.4)
        return box(key, w, d, h, (x, y, z), [fm, side_mat(key), top], rot_z=rz, bevel=0.0012)
    if kind == "bb":
        m = mat_img("bb_" + key, TEX + key + "_bb.png", cut=True, gloss=True)
        ob = plane(key, w, h, (x, y, z), m, rot=(0, 0, rz)); return ob
    if kind == "gen":
        name, (gw, gd, gh) = key
        fm = mat_img("gen_" + name, TEX + name + ".png", coord="FRONT")
        im = img(TEX + name + ".png"); px = list(im.pixels[0:4])
        sm = mat("genlado_" + name, (px[0], px[1], px[2]), rough=0.45)
        return box(name, gw, gd, gh, (x, y, z), [fm, sm, sm], rot_z=rz, bevel=0.0012)
    if kind == "jar":
        name, r, jh = key
        lm = mat_img("jar_" + name, TEX + name + ".png", coord="GEN", proj="TUBE", gloss=True)
        cap = mat("tampa_" + name, (0.95, 0.95, 0.95), rough=0.3)
        return cyl(name, r, jh, (x, y, z), [lm, cap])
    if kind == "bag":
        name, (bw, bd, bh) = key
        fm = mat_img("bag_" + name, TEX + name + ".png", coord="FRONT", rough=0.55)
        im = img(TEX + name + ".png"); px = list(im.pixels[0:4])
        sm = mat("baglado_" + name, (px[0], px[1], px[2]), rough=0.55)
        return box(name, bw, bd, bh, (x, y, z), [fm, sm, sm], rot_z=rz, bevel=0.018)

def fill(items, x0, x1, z, y_front, deep=2, gap=0.006, messy=None, rng=None, repeat=True, stack_low=True):
    """coloca itens da esquerda para a direita a partir da borda frontal, repetindo a sequência até
    encher a largura (como numa loja abastecida). messy: dict com falha/giro/recuo/caido."""
    x = x0 + 0.01; placed = []; seq = list(items); i = 0; guard = 0
    while seq and guard < 400:
        guard += 1
        it = seq[i % len(seq)]; i += 1
        kind, key = it[0], it[1]; n = it[2] if len(it) > 2 else 1
        w, d, h = dims(kind, key)
        stop = False
        for f in range(n):
            if x + w > x1 - 0.005: stop = True; break
            cx = x + w / 2
            skip = messy and rng.random() < messy.get("falha", 0)
            if not skip:
                layers = 1 if kind == "bb" else deep
                pilha = 2 if (stack_low and kind in ("box", "gen") and h < 0.085) else 1
                for k in range(layers):
                    for p in range(pilha):
                        y = y_front + 0.012 + d / 2 + k * (d + 0.004)
                        rz = 0.0; dy = 0.0
                        if messy:
                            rz = rng.uniform(-1, 1) * messy.get("giro", 0)
                            if k == 0 and rng.random() < messy.get("recuo", 0): dy = rng.uniform(0.05, 0.14)
                        if messy and k == 0 and p == 0 and rng.random() < messy.get("caido", 0) and kind == "box":
                            ob = product(kind, key, cx, y + 0.02, z)
                            ob.rotation_euler = (math.pi / 2, 0, rng.uniform(-0.5, 0.5)); ob.location.z = z + d / 2
                            break
                        product(kind, key, cx, y + dy, z + p * (h + 0.002), rz=rz)
            placed.append((cx, w, it))
            x += w + gap
        if stop or (not repeat and i >= len(seq)): break
    return placed

# ----------------------------------------------------------------- mobiliário
GRAY = None
def gondola(name, x0, n_mod, mod_w, y_back, depth, H, levels, rail_art=None, peg=True, dupla=False):
    """gôndola de parede voltada para -Y. levels = alturas das prateleiras (a primeira é o deck da base)"""
    panel = mat_img("chapa", TEX + "chapa.png", coord="GEN", proj="FLAT") if peg else mat("fundo", (0.84, 0.85, 0.86))
    if peg:
        nt = panel.node_tree; ti = [n for n in nt.nodes if n.type == "TEX_IMAGE"][0]; ti.extension = "REPEAT"
        mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (n_mod * mod_w * 14, H * 14, 1)
        tc = [n for n in nt.nodes if n.type == "TEX_COORD"][0]
        sp = nt.nodes.new("ShaderNodeSeparateXYZ"); cb = nt.nodes.new("ShaderNodeCombineXYZ")
        nt.links.new(tc.outputs["Generated"], sp.inputs[0]); nt.links.new(sp.outputs["X"], cb.inputs["X"]); nt.links.new(sp.outputs["Z"], cb.inputs["Y"])
        nt.links.new(cb.outputs[0], mp.inputs["Vector"]); nt.links.new(mp.outputs[0], ti.inputs["Vector"])
    W = n_mod * mod_w; xc = x0 + W / 2
    metal = mat("metal_claro", (0.90, 0.91, 0.92), rough=0.35, metal=0.2)
    escuro = mat("metal_escuro", (0.22, 0.23, 0.25), rough=0.4, metal=0.3)
    base = mat("rodape", (0.16, 0.17, 0.19), rough=0.5)
    rail = mat("trilho", (0.94, 0.94, 0.93), rough=0.3)
    box(name + "_fundo", W, 0.03, H, (xc, y_back + 0.015, 0), [panel, metal])
    for i in range(n_mod + 1):
        box(name + f"_coluna{i}", 0.035, 0.05, H, (x0 + i * mod_w, y_back + 0.0, 0), [escuro])
    for sx in (x0 - 0.012, x0 + W + 0.012):
        box(name + "_lateral", 0.024, depth + 0.02, H, (sx, y_back - depth / 2, 0), [metal])
    box(name + "_rodape", W, 0.02, 0.13, (xc, y_back - depth + 0.012, 0), [base])
    yf = y_back - depth
    shelves = []
    for j, z in enumerate(levels):
        for i in range(n_mod):
            mx = x0 + i * mod_w + mod_w / 2
            box(name + f"_prat{j}_{i}", mod_w - 0.012, depth, 0.022, (mx, y_back - depth / 2, z - 0.022), [metal])
            rm = rail
            if rail_art and rail_art.get((j, i)):
                rm = mat_img("regua_art", TEX + "arte_regua.png", coord="FRONT")
            box(name + f"_trilho{j}_{i}", mod_w - 0.012, 0.014, 0.042, (mx, yf - 0.006, z - 0.034), [rm, rail, rail])
        shelves.append(z)
    return {"x0": x0, "W": W, "yf": yf, "yb": y_back, "levels": shelves, "H": H, "mod_w": mod_w}

def price_tags(g, level_idx, xs, seed=0):
    rng = random.Random(seed)
    for k, x in enumerate(xs):
        m = mat_img(f"preco_{(seed + k) % 8}", TEX + f"preco_{(seed + k) % 8}.png")
        z = g["levels"][level_idx] - 0.031
        plane(f"preco{level_idx}_{k}", 0.058, 0.026, (x, g["yf"] - 0.0145, z), m)

def balcao(x0, x1, y0, y1, h=1.0):
    tampo = mat("tampo", (0.95, 0.95, 0.94), rough=0.25)
    frente = mat("balcao_frente", (0.42, 0.44, 0.47), rough=0.6)
    xc = (x0 + x1) / 2; yc = (y0 + y1) / 2
    box("balcao", x1 - x0, y1 - y0, h - 0.04, (xc, yc, 0), [frente, frente])
    box("tampo", x1 - x0 + 0.06, y1 - y0 + 0.06, 0.04, (xc, yc, h - 0.04), [tampo])
    return h

def pessoa(x, y, h=1.70):
    m = mat("manequim", (0.20, 0.28, 0.42), rough=0.55)
    cyl("pernas", 0.11, h * 0.47, (x, y, 0), [m]); cyl("tronco", 0.17, h * 0.33, (x, y, h * 0.47), [m])
    me = bpy.data.meshes.new("cabeca"); bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=0.105)
    bm.to_mesh(me); bm.free(); me.materials.append(m)
    for pg in me.polygons: pg.use_smooth = True
    ob = bpy.data.objects.new("cabeca", me); ob.location = (x, y, h - 0.105); link(ob)

# ----------------------------------------------------------------- materiais de PDV
def wobbler(x, y_front, z):
    haste = mat("haste", (0.92, 0.95, 0.97), rough=0.05, transm=0.9)
    box("haste_wob", 0.008, 0.10, 0.004, (x, y_front - 0.05, z), [haste])
    m = mat_img("wob", TEX + "arte_wobbler.png", cut=True, gloss=True)
    plane("wobbler", 0.11, 0.11, (x, y_front - 0.10, z - 0.045), m, rot=(math.radians(-6), 0, math.radians(8)))

def stopper(x, y_front, z):
    m = mat_img("stop", TEX + "arte_stopper.png", gloss=True)
    # placa perpendicular à gôndola (normal em X), visível dos dois lados do corredor
    plane("stopper_a", 0.20, 0.30, (x + 0.001, y_front - 0.115, z), m, rot=(0, 0, math.pi / 2))
    plane("stopper_b", 0.20, 0.30, (x - 0.001, y_front - 0.115, z), m, rot=(0, 0, -math.pi / 2))
    box("stopper_clip", 0.01, 0.03, 0.05, (x, y_front - 0.01, z + 0.10), [mat("clip", (0.3, 0.3, 0.3))])

def testeira(g):
    m = mat_img("test", TEX + "arte_testeira.png", coord="FRONT")
    box("testeira", g["W"], 0.025, 0.30, (g["x0"] + g["W"] / 2, g["yb"] - 0.04, g["H"] + 0.02), [m, mat("bordo", (0.03, 0.12, 0.28))])

def clip_strip(x, y, z_top, n=4):
    tira = mat("tira", (0.93, 0.96, 0.98), rough=0.1, transm=0.7)
    box("tira", 0.004, 0.035, 0.62, (x - 0.002, y, z_top - 0.62), [tira])
    hm = mat_img("clipcab", TEX + "arte_clipstrip.png")
    plane("clip_cab", 0.12, 0.09, (x - 0.006, y, z_top - 0.02), hm, rot=(0, 0, -math.pi / 2))
    for k in range(n):
        ob = product("box", "banni3_a" if k % 2 == 0 else "banni3_b", x - 0.016, y, z_top - 0.16 - k * 0.135)
        ob.rotation_euler = (0, 0, -math.pi / 2)

def display_balcao(x, y, z):
    papelao = mat("papelao_td", (0.79, 0.27, 0.34), rough=0.6)
    box("bandeja", 0.30, 0.20, 0.07, (x, y, z), [papelao])
    for r in range(2):
        for c in range(2):
            ob = product("box", ["topdog_a", "topdog_b"][c], x - 0.075 + c * 0.15, y - 0.05 + r * 0.06, z + 0.02)
            ob.scale = (1.0, 1.0, 1.0)
    m = mat_img("bal", TEX + "arte_balcao.png")
    plane("cab_balcao", 0.30, 0.17, (x, y + 0.09, z + 0.07), m, rot=(math.radians(-10), 0, 0))

def take_one(x, y, z):
    acr = mat("acrilico", (0.92, 0.96, 0.99), rough=0.02, alpha=0.22)
    borda = mat("acrilico_borda", (0.80, 0.86, 0.90), rough=0.05, alpha=0.55)
    box("to_base", 0.17, 0.09, 0.006, (x, y, z), [borda])
    box("to_fundo", 0.17, 0.005, 0.23, (x, y + 0.04, z), [acr])
    box("to_frente", 0.17, 0.005, 0.07, (x, y - 0.035, z), [acr])
    m = mat_img("folheto", TEX + "arte_takeone.png")
    for k in range(3):
        plane(f"folheto{k}", 0.14, 0.198, (x, y + 0.03 - k * 0.012, z + 0.008), m, rot=(math.radians(-9), 0, 0))

def display_chao(x, y, cheio=True):
    lat = mat_img("dc_lat", TEX + "arte_displaychao_lat.png", coord="GEN")
    cart = mat("papelao", (0.07, 0.47, 0.20), rough=0.6)
    W, D, H = 0.52, 0.40, 1.30
    for sx in (x - W / 2, x + W / 2): box("dc_lado", 0.012, D, H, (sx, y, 0), [lat, lat])
    box("dc_fundo", W, 0.012, H, (x, y + D / 2, 0), [cart])
    for k, z in enumerate((0.06, 0.48, 0.90)):
        box(f"dc_prat{k}", W, D, 0.02, (x, y, z - 0.02), [cart])
        if cheio:
            fill([("bb", "herbalvet", 3)], x - W / 2 + 0.01, x + W / 2, z, y - D / 2, deep=1, gap=0.02)
    m = mat_img("dc_cab", TEX + "arte_displaychao.png", coord="FRONT")
    box("dc_cab", W + 0.04, 0.02, 0.40, (x, y - D / 2 + 0.03, H), [m, cart])

def ilha(x, y, erro=False):
    art = "arte_cubo_wellpet.png" if erro else "arte_ilha.png"
    m = mat_img("cubo_" + ("erro" if erro else "ok"), TEX + art, coord="FRONT")
    s = 0.40
    for i in range(2):
        for j in range(2):
            for rz in (0,):
                box(f"cubo{i}{j}", s, s, s, (x - s / 2 + i * s, y - s / 2 + j * s, 0), [m, m, mat("cubo_topo", (0.95, 0.95, 0.94))])
    # laterais também impressas: gira cópias finas nas faces externas
    for (dx, dy, rz) in ((-s, 0, -math.pi / 2), (s, 0, math.pi / 2)):
        for j in range(2):
            ob = plane("cubo_lat", s, s, (x + dx, y - s / 2 + j * s, 0), m, rot=(0, 0, rz))
    top = 0.8 / 2 + 0.0
    fill([("bb", "herbalvet", 3)], x - 0.39, x + 0.4, s, y - 0.33, deep=1, gap=0.02)
    fill([("bb", "enziclim", 5)] if not erro else [("bb", "herbalvet", 3)], x - 0.39, x + 0.4, s, y + 0.02, deep=1, gap=0.03)

def cartaz(x, y, z):
    m = mat_img("cartaz", TEX + "arte_cartaz.png")
    moldura = mat("moldura", (0.12, 0.13, 0.15))
    box("moldura", 0.62, 0.012, 0.87, (x, y + 0.008, z - 0.013), [moldura])
    plane("cartaz", 0.594, 0.841, (x, y, z), m)

def adesivo(x, y, rz):
    m = mat_img("ades", TEX + "arte_adesivo.png", cut=True)
    floor_decal("adesivo", 0.62, (x, y, 0.001), m, rot_z=rz)

# ----------------------------------------------------------------- cena
def luzes():
    def area(name, loc, size, energy, rot=(0, 0, 0), sy=None, color=(1, 1, 1)):
        L = bpy.data.lights.new(name, "AREA"); L.energy = energy; L.color = color
        if sy: L.shape = "RECTANGLE"; L.size = size; L.size_y = sy
        else: L.size = size
        ob = bpy.data.objects.new(name, L); ob.location = loc; ob.rotation_euler = rot; link(ob)
    for x in (-2.0, 0.0, 2.0, 4.0):
        for y in (0.0, 1.6, 3.0):
            area(f"teto{x}{y}", (x, y, 3.3), 1.2, 38, sy=0.25, color=(1.0, 0.98, 0.95))
    area("chave", (1.0, -2.5, 2.8), 3.0, 210, rot=(math.radians(55), 0, 0))
    area("preench", (-3.5, -1.0, 2.0), 3.0, 70, rot=(math.radians(60), 0, math.radians(-50)))

def ambiente():
    piso = mat("piso", (0.60, 0.585, 0.55), rough=0.3)
    parede = mat("parede", (0.88, 0.88, 0.86), rough=0.9)
    faixa = mat("faixa_parede", (0.03, 0.13, 0.28), rough=0.8)
    floor_decal("piso", 30, (0, 0, 0), piso)
    box("parede_fundo", 12, 0.1, 3.4, (0.6, 3.65, 0), [parede, parede])
    box("parede_esq", 0.1, 6.0, 3.4, (-3.95, 0.7, 0), [parede, parede])
    box("faixa", 12, 0.012, 0.10, (0.6, 3.595, 2.62), [faixa])

def construir(v):
    """v: dict de variantes: estado ('ok'|'antes'), balcao(bool), extra ('certo'|'errado'|None),
    ilha ('ok'|'erro'|None), zonas(bool), pessoa(bool)"""
    rng = random.Random(11)
    ambiente(); luzes()
    P = {}
    # FARMÁCIA (estante atrás do balcão), 2 módulos, 7 níveis
    lv = [0.15, 0.42, 0.69, 0.96, 1.23, 1.50, 1.77]
    rail_art = {(3, 0): True} if v.get("regua") else None
    g = gondola("farm", 0.6, 2, 1.0, 3.55, 0.35, 2.05, lv, rail_art=rail_art)
    P["farm"] = g; yf = g["yf"]
    if v.get("testeira", True): testeira(g)
    antes = v.get("estado") == "antes"
    messy = {"falha": 0.34, "giro": 0.38, "recuo": 0.45, "caido": 0.24} if antes else None
    m1a, m1b, m2a, m2b, fim = 0.6, 1.1, 1.6, 2.1, 2.6
    GL = lambda nm, w, h: ("gen", (nm, (w, 0.03, h)))
    c_anti = [GL("gen_laranja", 0.085, 0.13), GL("gen_roxo", 0.07, 0.14), GL("gen_azul", 0.09, 0.12)]
    c_verm = [GL("gen_vinho", 0.12, 0.07), GL("gen_amarelo", 0.11, 0.065)]
    potes = [("jar", ("pote_azul", 0.045, 0.12)), ("jar", ("pote_laranja", 0.045, 0.12)), ("jar", ("pote_verde", 0.04, 0.10))]
    meds = [GL("gen_cinza", 0.075, 0.10), GL("gen_verdeagua", 0.075, 0.10), GL("gen_petroleo", 0.08, 0.11)]
    W = lambda *k: [("box", x) for x in k]
    # ordem de cada nível: (itens, x inicial, x final)
    plano = {
        6: [(W("leevre_a", "leevre_b"), m1a, m1b), (c_anti, m1b, m2a), ([("bb", "plenipil")], m2a, m2b), (potes, m2b, fim)],
        5: [(W("wellpet_a", "wellpet_b", "wellpet_c", "wellpet_d", "wellpet_e", "banni3_a", "banni3_b"), m1a, m1b), (c_anti, m1b, m2a), (W("topdog_a", "topdog_b", "topdog_c"), m2a, m2b), (c_verm, m2b, fim)],
        4: [(W("leevre_a", "leevre_b", "wellpet_d", "wellpet_e"), m1a, m1b), (c_anti, m1b, m2a), (W("topdog_a", "topdog_b", "topdog_c"), m2a, m2b), (c_verm, m2b, fim)],
        3: [(W("banni3_a", "banni3_b"), m1a, m1b), (c_anti, m1b, m2a), ([("bb", "plenipil")], m2a, m2b), (potes, m2b, fim)],
        2: [(W("wellpet_a", "wellpet_b", "wellpet_c"), m1a, m1b), (c_anti, m1b, m2a), (potes, m2a, m2b), (potes, m2b, fim)],
        1: [(c_anti, m1a, m1b), (meds, m1b, m2a), (meds, m2a, m2b), (meds, m2b, fim)],
        0: [(meds, m1a, m1b), (meds, m1b, m2a), (meds, m2a, m2b), (meds, m2b, fim)],
    }
    if antes:  # marcas misturadas: concorrente no meio do bloco, WellPET perdido no vermífugo
        plano[5][0] = ([("box", "wellpet_a"), c_anti[0], ("box", "wellpet_c"), ("box", "banni3_a"), c_anti[2], ("box", "wellpet_b")], m1a, m1b)
        plano[4][2] = ([("box", "topdog_a"), ("box", "wellpet_e"), ("box", "topdog_c"), ("box", "leevre_a")], m2a, m2b)
        plano[3][0] = ([("box", "banni3_b"), ("box", "wellpet_d"), c_anti[1]], m1a, m1b)
    for lvl, segs in plano.items():
        xs = []
        for items, a, b in segs:
            pl = fill(items, a, b, lv[lvl], yf, deep=2, messy=messy, rng=rng)
            seen = set()
            for cx, w, it in pl:
                k = (it[0], str(it[1]))
                if k not in seen: seen.add(k); xs.append(cx)
        if not antes: price_tags(g, lvl, xs, seed=lvl * 3)
        else: price_tags(g, lvl, [x for x in xs if rng.random() < 0.25], seed=lvl * 3)
    P["farm_blocos"] = {"antipulga": (0.85, yf, 1.62), "concorrente": (1.35, yf, 1.62), "vermifugo": (1.85, yf, 1.62), "suplementos": (1.85, yf, 1.06), "concorrente2": (2.35, yf, 1.62)}
    if v.get("wobbler_farm"): wobbler(0.74, yf, 1.53)
    if v.get("clip"): clip_strip(0.6 - 0.025, 3.36, 1.50)
    if v.get("zonas"):
        for nm, z0, z1, c in (("pes", 0.0, 0.6, (0.55, 0.58, 0.62)), ("maos", 0.6, 1.2, (0.0, 0.49, 0.76)), ("olhos", 1.2, 1.75, (0.06, 0.68, 0.19))):
            zm = mat("zona_" + nm, c, rough=1.0, alpha=0.20)
            plane("zona_" + nm, 1.02, z1 - z0, (1.1, yf - 0.03, z0), zm)
        pessoa(0.25, yf - 0.25)
    # BALCÃO / CAIXA
    if v.get("balcao", True):
        balcao(0.5, 2.7, 1.9, 2.5)
        tela = mat("tela", (0.05, 0.06, 0.08), rough=0.2)
        box("monitor", 0.36, 0.03, 0.26, (1.75, 2.3, 1.12), [tela]); box("pe_monitor", 0.06, 0.06, 0.12, (1.75, 2.32, 1.0), [tela])
        box("maquininha", 0.08, 0.14, 0.04, (2.0, 2.05, 1.0), [mat("maq", (0.15, 0.15, 0.16))])
        if v.get("display_balcao", True): display_balcao(0.95, 2.12, 1.0)
        if v.get("takeone", True): take_one(2.42, 2.18, 1.0)
    # ÁREA DE ESPERA + CARTAZ
    cartaz(3.25, 3.594, 1.35)
    box("banco", 1.2, 0.42, 0.44, (3.25, 3.30, 0), [mat("madeira", (0.55, 0.38, 0.24), rough=0.55)])
    # HIGIENE DO AMBIENTE (salão), 2 módulos
    lh = [0.15, 0.55, 0.95, 1.35]
    h = gondola("hig", -2.6, 2, 1.0, 3.55, 0.42, 1.8, lh)
    P["hig"] = h; yh = h["yf"]
    tapete = ("gen", ("gen_azul", (0.30, 0.12, 0.20)), 3); areia = ("bag", ("racao_mostarda", (0.26, 0.12, 0.34)), 3)
    desinf = [("jar", ("pote_verde", 0.05, 0.24), 3), ("jar", ("pote_azul", 0.05, 0.24), 3)]
    fill([tapete], -2.6, -1.6, lh[0], yh, deep=2); fill([areia], -1.6, -0.6, lh[0], yh, deep=2)
    fill([tapete], -2.6, -1.6, lh[1], yh, deep=2); fill([("gen", ("gen_petroleo", (0.28, 0.12, 0.22)), 3)], -1.6, -0.6, lh[1], yh, deep=2)
    fill(desinf, -2.6, -1.6, lh[2], yh, deep=2)
    buraco = v.get("extra") == "errado"
    herb = [] if buraco else [("bb", "herbalvet", 4)]
    fill(herb + [("bb", "enziclim", 3)], -1.6 + (0.6 if buraco else 0), -0.6, lh[2], yh, deep=1, gap=0.025)
    fill([("bb", "enziclim", 5)], -1.6, -0.6, lh[3], yh, deep=1, gap=0.03)
    fill(desinf, -2.6, -1.6, lh[3], yh, deep=2)
    price_tags(h, 2, [-1.5, -1.25, -0.9, -0.7] if not buraco else [-0.9, -0.7], seed=5)
    price_tags(h, 3, [-1.5, -1.1, -0.8], seed=6)
    P["hig_buraco"] = (-1.3, yh, lh[2] + 0.13)
    if v.get("stopper"): stopper(-1.62, yh, 1.42)
    if v.get("extra") in ("certo", "errado") or v.get("display_chao"):
        display_chao(-0.22, yh - 0.05, cheio=True); P["display"] = (-0.22, yh - 0.25, 1.0)
    # RAÇÃO (gôndola de corredor, voltada para a frente)
    lr = [0.15, 0.62, 1.09]
    r = gondola("rac", -2.75, 1, 1.5, 1.15, 0.45, 1.55, lr, peg=False)
    bags = [("bag", ("racao_vermelha", (0.32, 0.13, 0.44)), 2), ("bag", ("racao_azul", (0.32, 0.13, 0.44)), 2)]
    bags2 = [("bag", ("racao_verde", (0.30, 0.13, 0.40)), 2), ("bag", ("racao_mostarda", (0.30, 0.13, 0.40)), 2)]
    for k, z in enumerate(lr): fill(bags if k % 2 == 0 else bags2, -2.75, -1.25, z, r["yf"], deep=2, gap=0.03)
    if v.get("wobbler_racao"): wobbler(-1.78, r["yf"], 1.52)
    if v.get("stopper_racao"): stopper(-1.25, r["yf"], 1.2)
    P["rac"] = r
    # ILHA
    if v.get("ilha"): ilha(-0.55, 1.55, erro=v["ilha"] == "erro"); P["ilha"] = (-0.55, 1.55, 0.6)
    # ADESIVO
    if v.get("adesivo"): adesivo(-0.25, 0.65, math.radians(-38))
    return P

def camera(loc, target, lens=35, res=(1800, 1200)):
    sc = bpy.context.scene
    cam = bpy.data.cameras.new("cam"); cam.lens = lens; cam.sensor_width = 36
    ob = bpy.data.objects.new("cam", cam); link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    sc.camera = ob; sc.render.resolution_x = int(res[0] * SCALE); sc.render.resolution_y = int(res[1] * SCALE)
    sc.render.resolution_percentage = 100
    return ob

SH = {
    # estante da farmácia (sem o balcão na frente, vista didática)
    "F-DEPOIS":      ({"estado": "ok", "balcao": False, "testeira": False}, (1.1, 1.18, 1.02), (1.1, 3.4, 0.98), 35, (1200, 1600)),
    "F-ANTES":       ({"estado": "antes", "balcao": False, "testeira": False}, (1.1, 1.18, 1.02), (1.1, 3.4, 0.98), 35, (1200, 1600)),
    "F-GONDOLA-ZONAS": ({"estado": "ok", "balcao": False, "testeira": False, "zonas": True}, (0.85, 0.95, 1.05), (0.95, 3.4, 0.95), 32, (1400, 1600)),
    "F-PRATELEIRA-IDEAL": ({"estado": "ok", "balcao": False}, (1.6, 0.62, 1.18), (1.6, 3.4, 1.12), 35, (1600, 1600)),
    "F-MAT-WOBBLER": ({"estado": "ok", "balcao": False, "wobbler_farm": True}, (1.0, 2.38, 1.66), (0.78, 3.25, 1.52), 50, (1600, 1200)),
    "F-MAT-REGUA":   ({"estado": "ok", "balcao": False, "regua": True}, (1.05, 2.45, 1.08), (0.95, 3.3, 0.93), 45, (1600, 1100)),
    "F-MAT-TESTEIRA": ({"estado": "ok"}, (1.6, -0.6, 1.62), (1.6, 3.3, 1.55), 32, (1800, 1200)),
    "F-MAT-CLIPSTRIP": ({"estado": "ok", "clip": True}, (-0.18, 2.72, 1.28), (0.56, 3.36, 1.16), 45, (1400, 1500)),
    "F-MAT-DISPLAY-BALCAO": ({"estado": "ok"}, (0.80, 1.05, 1.42), (0.98, 2.18, 1.08), 45, (1600, 1200)),
    "F-MAT-TAKEONE": ({"estado": "ok"}, (2.6, 1.3, 1.34), (2.42, 2.2, 1.1), 50, (1400, 1200)),
    "F-MAT-CARTAZ":  ({"estado": "ok"}, (2.62, 1.05, 1.25), (3.25, 3.5, 1.05), 32, (1400, 1500)),
    "F-PONTO-EXTRA-CERTO": ({"estado": "ok", "extra": "certo"}, (0.80, 1.30, 1.58), (-1.0, 3.2, 0.98), 28, (1800, 1300)),
    "F-PONTO-EXTRA-ERRADO": ({"estado": "ok", "extra": "errado"}, (0.80, 1.30, 1.58), (-1.0, 3.2, 0.98), 28, (1800, 1300)),
    "F-MAT-DISPLAY-CHAO": ({"estado": "ok", "display_chao": True}, (0.22, 1.72, 1.38), (-0.3, 3.05, 0.86), 30, (1400, 1500)),
    "F-MAT-STOPPER": ({"estado": "ok", "stopper": True}, (-0.3, 2.36, 1.52), (-1.62, 3.0, 1.44), 42, (1600, 1200)),
    "F-MAT-ILHA":    ({"estado": "ok", "ilha": "ok"}, (1.10, 0.05, 1.50), (-0.45, 1.62, 0.42), 35, (1600, 1200)),
    "F-ERRO-CARNAVAL": ({"estado": "ok", "ilha": "erro"}, (1.10, 0.05, 1.50), (-0.45, 1.62, 0.42), 35, (1600, 1200)),
    "F-MAT-ADESIVO-CHAO": ({"estado": "ok", "adesivo": True}, (0.38, -0.32, 1.78), (-0.25, 0.75, 0.0), 35, (1600, 1200)),
    "F-CROSS-MERCH": ({"estado": "ok", "wobbler_racao": True, "stopper_racao": True}, (-1.18, -0.42, 1.52), (-1.8, 0.65, 1.22), 40, (1600, 1200)),
    "F-LOJA":        ({"estado": "ok", "ilha": "ok", "adesivo": True, "display_chao": True, "wobbler_racao": True}, (3.1, -2.3, 3.45), (-0.45, 2.05, 0.55), 22, (2000, 1250)),
}

# pontos a projetar por foto (para anotações na página)
def anchors(shot, P):
    a = {}
    if shot in ("F-GONDOLA-ZONAS",):
        g = P["farm"]
        for nm, z in (("pes_meio", 0.3), ("maos_meio", 0.9), ("olhos_meio", 1.47), ("lim_060", 0.6), ("lim_120", 1.2), ("lim_175", 1.75)):
            a[nm] = (1.62, g["yf"] - 0.03, z)
    if shot in ("F-PRATELEIRA-IDEAL", "F-DEPOIS", "F-ANTES"):
        for k, p in P["farm_blocos"].items(): a[k] = p
        a["zona_quente"] = (1.6, P["farm"]["yf"], 1.6)
    if shot.startswith("F-PONTO-EXTRA"):
        a["buraco"] = P["hig_buraco"]; a["display"] = P.get("display")
    return {k: v for k, v in a.items() if v}

def render(shot):
    v, loc, tgt, lens, res = SH[shot]
    sc = reset(); P = construir(v); cam = camera(loc, tgt, lens, res)
    sc.render.filepath = OUT + shot + ".png"; sc.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)
    pts = {}
    for k, co in anchors(shot, P).items():
        p = world_to_camera_view(sc, cam, Vector(co)); pts[k] = [round(p.x * 100, 2), round((1 - p.y) * 100, 2)]
    f = OUT + "anot.json"; data = json.load(open(f)) if os.path.exists(f) else {}
    data[shot] = pts; json.dump(data, open(f, "w"), indent=1)
    print("RENDERIZADO", shot, pts)

for s in SHOTS:
    if s not in SH: print("SHOT DESCONHECIDO", s); continue
    render(s)
