"""Loja-modelo Ourofino em 3D, versão fotorrealista (Blender 5.x, Cycles).
Uso:
  Blender -b --factory-startup -P tools/render/loja2.py -- --root <repo> --assets <pasta ourofino-3d> \
      --shots F-DEPOIS,F-ANTES --samples 384 [--scale 1.0]
Saída: assets/render/<SHOT>.png (16 bits) + assets/render/anot.json (pontos projetados 0-100%).
Assets de terceiros: Poly Haven (CC0): HDRI crosswalk, textura oak_veneer_01 e plastered_wall, modelos de plantas,
pendente, relógio, câmera, caixa de papelão e banqueta.
"""
import bpy, bmesh, json, math, os, random, sys
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def arg(n, d=None): return argv[argv.index(n) + 1] if n in argv else d
ROOT = arg("--root", os.getcwd()); AS = arg("--assets", "")
SHOTS = [s for s in arg("--shots", "F-DEPOIS").split(",") if s]
SAMPLES = int(arg("--samples", "384")); SCALE = float(arg("--scale", "1.0"))
TEX = os.path.join(ROOT, "assets/tex/"); OUT = arg("--out", os.path.join(ROOT, "assets/render/")).rstrip("/") + "/"
os.makedirs(OUT, exist_ok=True)
CAIXAS = json.load(open(TEX + "caixas.json"))
FONTE = os.path.expanduser("~/Library/Fonts/Lexend-SemiBold.ttf")
rng = random.Random(11)

# ================================================================ render / mundo
MATS = {}
def reset():
    MATS.clear(); bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene; sc.render.engine = "CYCLES"
    pr = bpy.context.preferences.addons["cycles"].preferences
    pr.compute_device_type = "METAL"; pr.get_devices()
    for d in pr.devices: d.use = d.type == "METAL"
    c = sc.cycles; c.device = "GPU"; c.samples = SAMPLES
    c.use_adaptive_sampling = True; c.adaptive_threshold = 0.012
    c.use_denoising = True
    c.max_bounces = 12; c.diffuse_bounces = 4; c.glossy_bounces = 6; c.transmission_bounces = 10; c.transparent_max_bounces = 24
    c.caustics_reflective = False; c.caustics_refractive = False
    c.sample_clamp_indirect = 8.0
    try:
        sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"
    except Exception: pass
    sc.view_settings.exposure = -1.15
    sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_depth = "16"
    w = bpy.data.worlds.new("mundo"); sc.world = w; w.use_nodes = True
    N = w.node_tree.nodes; L = w.node_tree.links; bg = N["Background"]
    hdr = os.path.join(AS, "hdri/crosswalk/crosswalk_2k.exr")
    if os.path.exists(hdr):
        et = N.new("ShaderNodeTexEnvironment"); et.image = bpy.data.images.load(hdr)
        mp = N.new("ShaderNodeMapping"); tc = N.new("ShaderNodeTexCoord")
        mp.inputs["Rotation"].default_value = (0, 0, math.radians(200))
        L.new(tc.outputs["Generated"], mp.inputs["Vector"]); L.new(mp.outputs[0], et.inputs["Vector"])
        L.new(et.outputs["Color"], bg.inputs["Color"]); bg.inputs["Strength"].default_value = 5.0
    return sc

def link(ob): bpy.context.scene.collection.objects.link(ob); return ob

def img(path, data=False):
    im = bpy.data.images.load(path, check_existing=True)
    if data: im.colorspace_settings.name = "Non-Color"
    return im

def P(m): return m.node_tree.nodes["Principled BSDF"]

def mat(name, rgb, rough=0.5, metal=0.0, alpha=1.0, emit=0.0, transm=0.0, coat=0.0, ior=1.45, aniso=0.0):
    if name in MATS: return MATS[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; p = P(m)
    p.inputs["Base Color"].default_value = (*rgb, 1); p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal; p.inputs["IOR"].default_value = ior
    if transm: p.inputs["Transmission Weight"].default_value = transm
    if coat: p.inputs["Coat Weight"].default_value = coat; p.inputs["Coat Roughness"].default_value = 0.06
    if aniso: p.inputs["Anisotropic"].default_value = aniso
    if emit: p.inputs["Emission Color"].default_value = (*rgb, 1); p.inputs["Emission Strength"].default_value = emit
    if alpha < 1: p.inputs["Alpha"].default_value = alpha
    MATS[name] = m; return m

def coords(nt, mode):
    N, L = nt.nodes, nt.links; tc = N.new("ShaderNodeTexCoord")
    if mode == "FRONT":  # projeção frontal (eixo -Y) em coordenadas geradas
        sp = N.new("ShaderNodeSeparateXYZ"); cb = N.new("ShaderNodeCombineXYZ")
        L.new(tc.outputs["Generated"], sp.inputs[0]); L.new(sp.outputs["X"], cb.inputs["X"]); L.new(sp.outputs["Z"], cb.inputs["Y"])
        return cb.outputs[0]
    return tc.outputs[{"GEN": "Generated", "UV": "UV", "OBJ": "Object"}[mode]]

def mat_img(name, path, coord="UV", proj="FLAT", rough=0.35, coat=0.0, cut=False, under=None, emit=0.0, sheen=False):
    """material com imagem. cut: recorta pelo alfa. under: material/cor que aparece onde o alfa é zero."""
    if name in MATS: return MATS[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N, L = nt.nodes, nt.links; p = P(m)
    p.inputs["Roughness"].default_value = rough
    if coat: p.inputs["Coat Weight"].default_value = coat; p.inputs["Coat Roughness"].default_value = 0.05
    ti = N.new("ShaderNodeTexImage"); ti.image = img(path); ti.projection = proj
    ti.extension = "CLIP" if proj == "FLAT" else "REPEAT"
    L.new(coords(nt, coord), ti.inputs["Vector"])
    if under is not None:  # mistura com cor de base onde não há imagem (frascos 3D)
        mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"
        mx.inputs["A"].default_value = (*under, 1)
        L.new(ti.outputs["Alpha"], mx.inputs["Factor"]); L.new(ti.outputs["Color"], mx.inputs["B"])
        L.new(mx.outputs["Result"], p.inputs["Base Color"])
    else:
        L.new(ti.outputs["Color"], p.inputs["Base Color"])
    if emit:
        L.new(ti.outputs["Color"], p.inputs["Emission Color"]); p.inputs["Emission Strength"].default_value = emit
    if cut:
        gt = N.new("ShaderNodeMath"); gt.operation = "GREATER_THAN"; gt.inputs[1].default_value = 0.5
        L.new(ti.outputs["Alpha"], gt.inputs[0]); L.new(gt.outputs[0], p.inputs["Alpha"])
    # microtextura de cartão/papel
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 900; nz.inputs["Detail"].default_value = 2
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.025
    L.new(nz.outputs["Fac"], bp.inputs["Height"]); L.new(bp.outputs["Normal"], p.inputs["Normal"])
    MATS[name] = m; return m

def mat_pbr(name, folder, res, size_m, tint=None, rough_mul=1.0, norm=0.6, sat=1.0, val=1.0):
    if name in MATS: return MATS[name]
    base = os.path.join(AS, "texture", folder, f"{folder}_")
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N, L = nt.nodes, nt.links; p = P(m)
    tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1 / size_m,) * 3
    L.new(tc.outputs["Object"], mp.inputs["Vector"])
    def tex(sfx, data):
        t = N.new("ShaderNodeTexImage"); t.image = img(base + f"{sfx}_{res}.jpg", data); t.projection = "BOX"; t.projection_blend = 0.2
        L.new(mp.outputs[0], t.inputs["Vector"]); return t
    d = tex("diff", False); r = tex("rough", True); n = tex("nor_gl", True)
    hs = N.new("ShaderNodeHueSaturation"); hs.inputs["Saturation"].default_value = sat; hs.inputs["Value"].default_value = val
    L.new(d.outputs["Color"], hs.inputs["Color"])
    if tint:
        mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs["Factor"].default_value = 1.0
        L.new(hs.outputs[0], mx.inputs["A"]); mx.inputs["B"].default_value = (*tint, 1); L.new(mx.outputs["Result"], p.inputs["Base Color"])
    else: L.new(hs.outputs[0], p.inputs["Base Color"])
    mu = N.new("ShaderNodeMath"); mu.operation = "MULTIPLY"; mu.inputs[1].default_value = rough_mul
    L.new(r.outputs["Color"], mu.inputs[0]); L.new(mu.outputs[0], p.inputs["Roughness"])
    nm = N.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = norm
    L.new(n.outputs["Color"], nm.inputs["Color"]); L.new(nm.outputs[0], p.inputs["Normal"])
    MATS[name] = m; return m

def mat_porcelanato():
    m = bpy.data.materials.new("porcelanato"); m.use_nodes = True; nt = m.node_tree; N, L = nt.nodes, nt.links; p = P(m)
    tc = N.new("ShaderNodeTexCoord"); br = N.new("ShaderNodeTexBrick")
    br.offset = 0.0; br.squash = 1.0
    br.inputs["Scale"].default_value = 1.0; br.inputs["Brick Width"].default_value = 0.6; br.inputs["Row Height"].default_value = 0.6
    br.inputs["Mortar Size"].default_value = 0.0022; br.inputs["Mortar Smooth"].default_value = 0.2; br.inputs["Bias"].default_value = 0
    br.inputs["Color1"].default_value = (0.58, 0.58, 0.565, 1); br.inputs["Color2"].default_value = (0.545, 0.545, 0.53, 1)
    br.inputs["Mortar"].default_value = (0.33, 0.33, 0.32, 1)
    L.new(tc.outputs["Object"], br.inputs["Vector"])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 6; nz.inputs["Detail"].default_value = 6
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "OVERLAY"; mx.inputs["Factor"].default_value = 0.10
    L.new(br.outputs["Color"], mx.inputs["A"]); L.new(nz.outputs["Color"], mx.inputs["B"]); L.new(mx.outputs["Result"], p.inputs["Base Color"])
    mr = N.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value = 0.05; mr.inputs["To Max"].default_value = 0.15
    L.new(nz.outputs["Fac"], mr.inputs["Value"])
    mx2 = N.new("ShaderNodeMath"); mx2.operation = "MAXIMUM"; L.new(mr.outputs[0], mx2.inputs[0])
    inv = N.new("ShaderNodeMath"); inv.operation = "MULTIPLY"; inv.inputs[1].default_value = 0.6
    L.new(br.outputs["Fac"], inv.inputs[0]); L.new(inv.outputs[0], mx2.inputs[1]); L.new(mx2.outputs[0], p.inputs["Roughness"])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.35; bp.invert = True
    L.new(br.outputs["Fac"], bp.inputs["Height"]); L.new(bp.outputs["Normal"], p.inputs["Normal"])
    return m

def mat_vidro(name="vidro", tint=(0.92, 0.96, 0.98)):
    if name in MATS: return MATS[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N, L = nt.nodes, nt.links
    for n in list(N):
        if n.type == "BSDF_PRINCIPLED": N.remove(n)
    gl = N.new("ShaderNodeBsdfGlass"); gl.inputs["Color"].default_value = (*tint, 1); gl.inputs["Roughness"].default_value = 0.0; gl.inputs["IOR"].default_value = 1.5
    tr = N.new("ShaderNodeBsdfTransparent"); lp = N.new("ShaderNodeLightPath"); mx = N.new("ShaderNodeMixShader")
    L.new(lp.outputs["Is Shadow Ray"], mx.inputs[0]); L.new(gl.outputs[0], mx.inputs[1]); L.new(tr.outputs[0], mx.inputs[2])
    L.new(mx.outputs[0], N["Material Output"].inputs["Surface"]); MATS[name] = m; return m

def mat_plastico(name, rgb, transm=0.0, rough=0.25, sss=0.0):
    if name in MATS: return MATS[name]
    m = mat(name, rgb, rough=rough, transm=transm, coat=0.15)
    if sss: P(m).inputs["Subsurface Weight"].default_value = sss
    return m

# ================================================================ primitivas
def box(name, w, d, h, loc, mats, rz=0.0, bevel=0.0, seg=2):
    me = bpy.data.meshes.new(name); bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co.x *= w; v.co.y *= d; v.co.z = (v.co.z + 0.5) * h
    bm.to_mesh(me); bm.free(); ob = bpy.data.objects.new(name, me)
    for m in mats: me.materials.append(m)
    for pg in me.polygons:
        n = pg.normal
        if n.y < -0.9: pg.material_index = 0
        elif n.z > 0.9 and len(mats) > 2: pg.material_index = 2
        else: pg.material_index = min(1, len(mats) - 1)
    ob.location = loc; ob.rotation_euler = (0, 0, rz)
    if bevel:
        b = ob.modifiers.new("bev", "BEVEL"); b.width = bevel; b.segments = seg; b.limit_method = "ANGLE"; b.harden_normals = False
    return link(ob)

def plane(name, w, h, loc, m, rot=(0, 0, 0)):
    me = bpy.data.meshes.new(name)
    me.from_pydata([(-w / 2, 0, 0), (w / 2, 0, 0), (w / 2, 0, h), (-w / 2, 0, h)], [], [(0, 1, 2, 3)]); me.update()
    uv = me.uv_layers.new()
    for i, c in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]): uv.data[i].uv = c
    if me.polygons[0].normal.y > 0: me.flip_normals()
    me.materials.append(m); ob = bpy.data.objects.new(name, me); ob.location = loc; ob.rotation_euler = rot
    return link(ob)

def chao_plano(name, sx, sy, loc, m, z_up=True):
    me = bpy.data.meshes.new(name); a, b = sx / 2, sy / 2
    me.from_pydata([(-a, -b, 0), (a, -b, 0), (a, b, 0), (-a, b, 0)], [], [(0, 1, 2, 3)]); me.update()
    uv = me.uv_layers.new()
    for i, c in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]): uv.data[i].uv = c
    if not z_up: me.flip_normals()
    me.materials.append(m); ob = bpy.data.objects.new(name, me); ob.location = loc; return link(ob)

def cyl(name, r, h, loc, mats, seg=48, r2=None, sy=1.0, bevel=0.002, smooth=True):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r2 if r2 is not None else r, depth=h)
    for v in bm.verts: v.co.z += h / 2; v.co.y *= sy
    bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    for pg in me.polygons:
        pg.material_index = 1 if (abs(pg.normal.z) > 0.9 and len(mats) > 1) else 0
        pg.use_smooth = smooth and abs(pg.normal.z) < 0.9
    ob = bpy.data.objects.new(name, me); ob.location = loc
    if bevel: b = ob.modifiers.new("b", "BEVEL"); b.width = bevel; b.segments = 2; b.limit_method = "ANGLE"
    return link(ob)

def texto(txt, size, loc, m, rot=(math.radians(90), 0, 0), ext=0.008, align="CENTER"):
    cu = bpy.data.curves.new("txt", "FONT"); cu.body = txt; cu.size = size; cu.extrude = ext
    cu.font = bpy.data.fonts.load(FONTE, check_existing=True); cu.align_x = align; cu.align_y = "CENTER"
    ob = bpy.data.objects.new("txt", cu); ob.data.materials.append(m); ob.location = loc; ob.rotation_euler = rot
    return link(ob)

def importar(nome, loc, keep=None, rz=0.0, escala=1.0, top=False):
    """importa gltf do Poly Haven, mantém objetos cujo nome contém algum item de keep e
    coloca o pé (ou o topo, se top=True) no ponto loc."""
    f = os.path.join(AS, "model", nome, f"{nome}_1k.gltf")
    if not os.path.exists(f): print("SEM ASSET", nome); return []
    antes = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=f)
    novos = [o for o in bpy.data.objects if o not in antes]
    for o in novos:
        if o.type == "MESH" and keep and not any(k in o.name for k in keep):
            bpy.data.objects.remove(o, do_unlink=True)
    novos = [o for o in bpy.data.objects if o not in antes and o.type == "MESH"]
    if not novos: return []
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in novos for c in o.bound_box]
    mn = Vector(map(min, *pts)); mx = Vector(map(max, *pts)); c = (mn + mx) / 2
    ref = Vector((c.x, c.y, mx.z if top else mn.z))
    piv = bpy.data.objects.new("piv_" + nome, None); link(piv); piv.location = ref
    bpy.context.view_layer.update()
    for o in novos:
        o.parent = piv; o.matrix_parent_inverse = piv.matrix_world.inverted()
    piv.location = loc; piv.rotation_euler = (0, 0, rz); piv.scale = (escala,) * 3
    return novos

# ================================================================ produtos
def dims(kind, key):
    if kind == "box": return CAIXAS[key]["dims"]
    if kind == "h3": return {"herbalvet": (0.13, 0.09, 0.29), "enziclim": (0.10, 0.065, 0.26), "plenipil": (0.075, 0.075, 0.10)}[key]
    if kind == "gen": return key[1]
    if kind == "jar": return (key[1] * 2, key[1] * 2, key[2])
    if kind == "bag": return key[1]
    if kind == "frasco": return (key[1] * 2, key[1] * 2 * 0.7, key[2])

def caixa_ouro(key, x, y, z, rz=0.0):
    w, d, h = dims("box", key)
    fm = mat_img("frente_" + key, TEX + key + "_front.png", coord="FRONT", rough=0.3, coat=0.35)
    sc = CAIXAS[key]["side"]
    lado = mat("lado_" + key, tuple(sc), rough=0.32, coat=0.3)
    topo = mat("topo_" + key, tuple(min(1, c * 1.06 + 0.04) for c in sc), rough=0.32, coat=0.3)
    return box(key, w, d, h, (x, y, z), [fm, lado, topo], rz=rz, bevel=0.0014)

def herbalvet_3d(x, y, z, rz=0.0):
    verde = mat_plastico("herb_plast", (0.06, 0.42, 0.12), transm=0.35, rough=0.18, sss=0.2)
    corpo = mat_img("herb_corpo", TEX + "herbalvet_corpo.png", coord="FRONT", rough=0.2, coat=0.4, under=(0.06, 0.42, 0.12))
    tampa = mat("herb_tampa", (0.02, 0.22, 0.06), rough=0.35)
    W, D = 0.13, 0.085
    b = box("herb", W, D, 0.19, (x, y, z), [corpo, verde, verde], rz=rz, bevel=0.022, seg=5)
    sh = cyl("herb_ombro", 0.058, 0.055, (x - 0.012, y, z + 0.19), [verde, verde], r2=0.022, sy=0.72)
    cyl("herb_gargalo", 0.019, 0.02, (x - 0.012, y, z + 0.245), [verde, verde])
    cyl("herb_tampa", 0.023, 0.03, (x - 0.012, y, z + 0.262), [tampa, tampa], seg=24)
    me = bpy.data.meshes.new("alca"); bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=False, radius=0.03, segments=32); bm.to_mesh(me); bm.free()
    alca = bpy.data.objects.new("alca", me); alca.location = (x + 0.04, y, z + 0.205); alca.rotation_euler = (math.radians(90), 0, rz)
    link(alca); s = alca.modifiers.new("s", "SKIN"); me.materials.append(verde)
    for v in me.skin_vertices[0].data: v.radius = (0.008, 0.008)
    alca.modifiers.new("sub", "SUBSURF").levels = 1
    return b

def enziclim_3d(x, y, z, rz=0.0):
    branco = mat_plastico("enz_branco", (0.93, 0.94, 0.95), rough=0.22, sss=0.15)
    corpo = mat_img("enz_corpo", TEX + "enziclim_corpo.png", coord="FRONT", rough=0.22, coat=0.3, under=(0.93, 0.94, 0.95))
    verde = mat("enz_verde", (0.05, 0.45, 0.25), rough=0.3)
    b = cyl("enz", 0.045, 0.175, (x, y, z), [corpo, branco], sy=0.68)
    cyl("enz_ombro", 0.045, 0.03, (x, y, z + 0.175), [branco, branco], r2=0.016, sy=0.68)
    cyl("enz_rosca", 0.017, 0.018, (x, y, z + 0.205), [verde, verde])
    box("enz_cabeca", 0.028, 0.072, 0.04, (x, y - 0.014, z + 0.222), [branco], rz=rz, bevel=0.006, seg=3)
    cyl("enz_bico", 0.006, 0.02, (x, y - 0.052, z + 0.245), [verde, verde]).rotation_euler = (math.radians(90), 0, 0)
    g = box("enz_gatilho", 0.016, 0.012, 0.05, (x, y - 0.04, z + 0.18), [verde], bevel=0.003)
    g.rotation_euler = (math.radians(-14), 0, 0)
    return b

def plenipil_3d(x, y, z, rz=0.0):
    corpo = mat_img("plen_corpo", TEX + "plenipil_corpo.png", coord="FRONT", rough=0.25, coat=0.35, under=(0.93, 0.36, 0.55))
    tampa = mat("plen_tampa", (0.94, 0.94, 0.93), rough=0.3)
    b = cyl("plen", 0.036, 0.078, (x, y, z), [corpo, tampa])
    t = cyl("plen_tampa", 0.039, 0.024, (x, y, z + 0.078), [tampa, tampa])
    return b

def generico(key, x, y, z, rz=0.0):
    name, (w, d, h) = key
    fm = mat_img("g_" + name, TEX + f"g2_{name}.png", coord="FRONT", rough=0.32, coat=0.25)
    im = img(TEX + f"g2_{name}.png"); W, H = im.size; px = im.pixels
    i = (int(H * 0.5) * W + int(W * 0.03)) * 4
    lado = mat("glado_" + name, (px[i], px[i + 1], px[i + 2]), rough=0.35, coat=0.2)
    return box(name, w, d, h, (x, y, z), [fm, lado, lado], rz=rz, bevel=0.0014)

def pote(key, x, y, z, rz=0.0):
    name, r, h = key
    lm = mat_img("pote_" + name, TEX + f"g2_{name}.png", coord="GEN", proj="TUBE", rough=0.25, coat=0.3)
    tampa = mat("tampa_branca", (0.95, 0.95, 0.94), rough=0.28)
    b = cyl(name, r, h * 0.82, (x, y, z), [lm, tampa]); b.rotation_euler = (0, 0, rz + math.radians(rng.uniform(-25, 25)))
    cyl(name + "_tampa", r * 1.05, h * 0.18, (x, y, z + h * 0.82), [tampa, tampa], seg=32)
    return b

def frasco(key, x, y, z, rz=0.0):
    name, r, h = key
    lm = mat_img("fr_" + name, TEX + f"g2_{name}.png", coord="GEN", proj="TUBE", rough=0.25, coat=0.3)
    br = mat_plastico("fr_branco", (0.94, 0.94, 0.95), rough=0.22)
    tp = mat("fr_tampa_" + name, (0.1, 0.25, 0.55) if "azul" in name else (0.45, 0.3, 0.65), rough=0.3)
    b = cyl(name, r, h * 0.72, (x, y, z), [lm, br], sy=0.7)
    cyl(name + "_omb", r, h * 0.14, (x, y, z + h * 0.72), [br, br], r2=r * 0.4, sy=0.7)
    cyl(name + "_tp", r * 0.42, h * 0.12, (x, y, z + h * 0.86), [tp, tp], seg=24)
    return b

def saco(key, x, y, z, rz=0.0, nome_tex=None):
    name, (w, d, h) = key
    me = bpy.data.meshes.new(name); bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=8, use_grid_fill=True)
    for v in bm.verts:
        u, s, t = v.co.x * 2, v.co.y * 2, v.co.z + 0.5  # u,s em -1..1, t em 0..1
        puff = (1 - u * u) * (1 - (2 * t - 1) ** 2)
        v.co.x *= w; v.co.z = t * h
        v.co.y = s * d / 2 * (1 + 0.55 * puff)
        if t > 0.93: v.co.y *= 0.25  # selagem no topo
        if t < 0.04: v.co.y *= 0.92
    bm.to_mesh(me); bm.free()
    fm = mat_img("saco_" + name, TEX + f"g2_{name}.png", coord="FRONT", rough=0.38, coat=0.3)
    im = img(TEX + f"g2_{name}.png"); W, H = im.size; px = im.pixels; i = (int(H * 0.5) * W + 2) * 4
    lado = mat("sacolado_" + name, (px[i], px[i + 1], px[i + 2]), rough=0.4, coat=0.25)
    me.materials.append(fm); me.materials.append(lado)
    for pg in me.polygons: pg.material_index = 0 if pg.normal.y < -0.3 else 1; pg.use_smooth = True
    ob = bpy.data.objects.new(name, me); ob.location = (x, y, z); ob.rotation_euler = (0, 0, rz)
    return link(ob)

def product(kind, key, x, y, z, rz=0.0):
    if kind == "box": return caixa_ouro(key, x, y, z, rz)
    if kind == "h3": return {"herbalvet": herbalvet_3d, "enziclim": enziclim_3d, "plenipil": plenipil_3d}[key](x, y, z, rz)
    if kind == "gen": return generico(key, x, y, z, rz)
    if kind == "jar": return pote(key, x, y, z, rz)
    if kind == "frasco": return frasco(key, x, y, z, rz)
    if kind == "bag": return saco(key, x, y, z, rz)

def fill(items, x0, x1, z, y_front, deep=2, gap=0.006, messy=None, repeat=True):
    x = x0 + 0.01; placed = []; seq = list(items); i = 0; guard = 0
    while seq and guard < 400:
        guard += 1; it = seq[i % len(seq)]; i += 1
        kind, key = it[0], it[1]; n = it[2] if len(it) > 2 else 1
        w, d, h = dims(kind, key); stop = False
        for f in range(n):
            if x + w > x1 - 0.005: stop = True; break
            cx = x + w / 2
            if not (messy and rng.random() < messy.get("falha", 0)):
                layers = 1 if kind in ("h3",) else deep
                pilha = 2 if (kind in ("box", "gen") and h < 0.085) else 1
                for k in range(layers):
                    for p in range(pilha):
                        y = y_front + 0.016 + d / 2 + k * (d + 0.004)
                        rz = rng.uniform(-0.012, 0.012); dy = 0.0
                        if messy:
                            rz = rng.uniform(-1, 1) * messy.get("giro", 0)
                            if k == 0 and rng.random() < messy.get("recuo", 0): dy = rng.uniform(0.05, 0.14)
                        if messy and k == 0 and p == 0 and kind == "box" and rng.random() < messy.get("caido", 0):
                            ob = product(kind, key, cx, y + 0.02, z)
                            ob.rotation_euler = (math.pi / 2, 0, rng.uniform(-0.6, 0.6)); ob.location.z = z + d / 2
                            break
                        product(kind, key, cx, y + dy, z + p * (h + 0.0015), rz=rz)
            placed.append((cx, w, it)); x += w + gap
        if stop or (not repeat and i >= len(seq)): break
    return placed

# ================================================================ loja (casca)
def casca(v):
    piso = mat_porcelanato()
    chao_plano("piso", 8.2, 7.0, (0, 0.3, 0), piso)
    parede = mat_pbr("parede", "plastered_wall", "2k", 2.0, tint=(0.94, 0.93, 0.90), rough_mul=1.0, norm=0.25, sat=0.15, val=1.25)
    navy = mat("tinta_navy", (0.018, 0.06, 0.15), rough=0.85)
    rodape = mat("rodape_parede", (0.22, 0.23, 0.25), rough=0.4)
    teto = mat("teto", (0.93, 0.93, 0.92), rough=0.92)
    box("parede_fundo", 8.2, 0.12, 3.2, (0, 3.71, 0), [parede, parede])
    box("painel_farmacia", 2.6, 0.02, 3.2, (1.6, 3.645, 0), [navy, navy])
    box("parede_dir", 0.12, 7.0, 3.2, (4.06, 0.3, 0), [parede, parede])
    box("parede_frente", 8.2, 0.12, 3.2, (0, -3.2, 0), [parede, parede])
    for (nm, w, d, loc) in (("rod_f", 8.2, 0.015, (0, 3.64, 0)), ("rod_d", 0.015, 7.0, (3.995, 0.3, 0))):
        box(nm, w, d, 0.09, loc, [rodape])
    if v.get("teto", True):
        chao_plano("teto", 8.2, 7.0, (0, 0.3, 3.2), teto, z_up=False)
        painel = mat("led_painel", (1.0, 0.97, 0.92), rough=0.5, emit=6.0)
        for x in (-3.0, -1.5, 0.0, 1.5, 3.0):
            for y in (-1.6, 0.0, 1.5, 2.9):
                chao_plano("led", 0.6, 0.6, (x, y, 3.195), painel, z_up=False)
                L = bpy.data.lights.new("p", "AREA"); L.shape = "SQUARE"; L.size = 0.6; L.energy = 32; L.color = (1.0, 0.96, 0.9)
                o = bpy.data.objects.new("p", L); o.location = (x, y, 3.19); o.visible_camera = False; link(o)
    # vitrine na parede esquerda (x = -4.1): mureta, caixilhos, vidro, porta
    alu = mat("aluminio", (0.08, 0.085, 0.09), rough=0.3, metal=0.9)
    box("mureta", 0.12, 7.0, 0.45, (-4.06, 0.3, 0), [parede, parede])
    box("verga", 0.12, 7.0, 0.5, (-4.06, 0.3, 2.7), [parede, parede])
    for yy in (-3.1, -1.9, -0.7, 0.5, 1.7, 2.9, 3.62):
        box("montante", 0.07, 0.06, 2.25, (-4.06, yy, 0.45), [alu])
    box("travessa", 0.07, 7.0, 0.05, (-4.06, 0.3, 0.45), [alu]); box("travessa2", 0.07, 7.0, 0.05, (-4.06, 0.3, 2.65), [alu])
    vidro = mat_vidro()
    box("vidro", 0.012, 7.0, 2.2, (-4.06, 0.3, 0.47), [vidro, vidro])
    # sol entrando pela vitrine
    S = bpy.data.lights.new("sol", "SUN"); S.energy = 9.0; S.angle = math.radians(0.6); S.color = (1.0, 0.92, 0.80)
    so = bpy.data.objects.new("sol", S); link(so)
    dirv = Vector((0.80, 0.30, -0.42)).normalized(); so.rotation_euler = dirv.to_track_quat("-Z", "Y").to_euler()
    try:
        po = bpy.data.lights.new("portal", "AREA"); po.shape = "RECTANGLE"; po.size = 2.2; po.size_y = 7.0; po.cycles.is_portal = True
        pob = bpy.data.objects.new("portal", po); pob.location = (-3.98, 0.3, 1.57); pob.rotation_euler = (0, math.radians(-90), 0); link(pob)
    except Exception: pass

def placa_suspensa(txt, x, y, larg=1.25):
    navy = mat("placa_navy", (0.02, 0.07, 0.17), rough=0.45, coat=0.4)
    branco = mat("placa_txt", (1, 1, 1), rough=0.4, emit=0.4)
    verde = mat("placa_verde", (0.06, 0.68, 0.19), rough=0.4)
    z = 2.55
    box("placa", larg, 0.025, 0.30, (x, y, z), [navy, navy], bevel=0.01, seg=3)
    box("placa_faixa", larg, 0.027, 0.03, (x, y, z), [verde, verde])
    for s in (-1, 1):
        texto(txt, 0.13, (x, y - s * 0.014, z + 0.165), branco, rot=(math.radians(90), 0, 0 if s > 0 else math.pi), ext=0.002)
    cabo = mat("cabo", (0.2, 0.2, 0.2), rough=0.4, metal=0.8)
    for dx in (-larg / 2 + 0.08, larg / 2 - 0.08): cyl("cabo", 0.0015, 3.2 - z - 0.3, (x + dx, y, z + 0.3), [cabo, cabo], seg=8, bevel=0)

def trilho_spots(alvos):
    preto = mat("spot_preto", (0.03, 0.03, 0.035), rough=0.35, metal=0.6)
    for (pos, alvo) in alvos:
        cyl("spot", 0.035, 0.12, (pos[0], pos[1], pos[2] - 0.12), [preto, preto], seg=24)
        L = bpy.data.lights.new("spot", "SPOT"); L.energy = 330; L.spot_size = math.radians(44); L.spot_blend = 0.55
        L.shadow_soft_size = 0.04; L.color = (1.0, 0.9, 0.78)
        o = bpy.data.objects.new("spot", L); o.location = (pos[0], pos[1], pos[2] - 0.13); link(o)
        o.rotation_euler = (Vector(alvo) - o.location).to_track_quat("-Z", "Y").to_euler()

# ================================================================ mobiliário
def gondola(name, x0, n_mod, mod_w, y_back, depth, H, levels, led=False, rail_art=None, peg=True):
    branco = mat("aco_branco", (0.90, 0.905, 0.91), rough=0.28, coat=0.25)
    escuro = mat("aco_escuro", (0.16, 0.17, 0.19), rough=0.38, metal=0.5)
    inox = mat("inox", (0.62, 0.63, 0.65), rough=0.32, metal=1.0, aniso=0.6)
    W = n_mod * mod_w; xc = x0 + W / 2; yf = y_back - depth
    if peg:
        fundo = mat_img("chapa", TEX + "chapa.png", coord="OBJ", proj="FLAT", rough=0.35)
        nt = fundo.node_tree; ti = [n for n in nt.nodes if n.type == "TEX_IMAGE"][0]; ti.extension = "REPEAT"
        mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (32, 32, 32)
        tc = [n for n in nt.nodes if n.type == "TEX_COORD"][0]
        sp = nt.nodes.new("ShaderNodeSeparateXYZ"); cb = nt.nodes.new("ShaderNodeCombineXYZ")
        nt.links.new(tc.outputs["Object"], sp.inputs[0]); nt.links.new(sp.outputs["X"], cb.inputs["X"]); nt.links.new(sp.outputs["Z"], cb.inputs["Y"])
        nt.links.new(cb.outputs[0], mp.inputs["Vector"]); nt.links.new(mp.outputs[0], ti.inputs["Vector"])
        bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.6
        nt.links.new(ti.outputs["Color"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], P(fundo).inputs["Normal"])
    else: fundo = branco
    box(name + "_fundo", W, 0.03, H, (xc, y_back + 0.015, 0), [fundo, branco])
    for i in range(n_mod + 1): box(name + f"_col{i}", 0.04, 0.05, H, (x0 + i * mod_w, y_back, 0), [escuro], bevel=0.003)
    for sx in (x0 - 0.014, x0 + W + 0.014):
        box(name + "_lat", 0.028, depth + 0.02, H, (sx, y_back - depth / 2, 0), [branco], bevel=0.006, seg=3)
    box(name + "_rodape", W, 0.02, 0.13, (xc, yf + 0.012, 0), [inox], bevel=0.002)
    acril = mat("acrilico_trilho", (0.95, 0.97, 0.99), rough=0.02, transm=1.0, ior=1.49)
    trilho = mat("trilho", (0.95, 0.95, 0.94), rough=0.3)
    led_m = mat("fita_led", (1.0, 0.93, 0.82), rough=0.5, emit=22.0)
    for j, z in enumerate(levels):
        for i in range(n_mod):
            mx = x0 + i * mod_w + mod_w / 2
            box(f"{name}_pr{j}_{i}", mod_w - 0.014, depth, 0.022, (mx, y_back - depth / 2, z - 0.022), [branco], bevel=0.003)
            rm = trilho
            if rail_art and rail_art.get((j, i)): rm = mat_img("regua_art", TEX + "arte_regua.png", coord="FRONT", rough=0.3, coat=0.3)
            box(f"{name}_tr{j}_{i}", mod_w - 0.014, 0.012, 0.044, (mx, yf - 0.005, z - 0.036), [rm, trilho, trilho], bevel=0.0015)
            box(f"{name}_ac{j}_{i}", mod_w - 0.014, 0.003, 0.046, (mx, yf - 0.0205, z - 0.037), [acril])
            if led and j > 0:
                box(f"{name}_led{j}_{i}", mod_w - 0.04, 0.008, 0.005, (mx, yf + 0.02, z - 0.029), [led_m])
    return {"x0": x0, "W": W, "yf": yf, "yb": y_back, "levels": levels, "H": H}

def price_tags(g, lvl, xs, seed=0):
    for k, x in enumerate(xs):
        m = mat_img(f"preco_{(seed + k) % 8}", TEX + f"preco_{(seed + k) % 8}.png", rough=0.4)
        plane(f"pr{lvl}_{k}", 0.058, 0.026, (x, g["yf"] - 0.0118, g["levels"][lvl] - 0.033), m)

def balcao(x0, x1, y0, y1, h=1.0):
    madeira = mat_pbr("carvalho", "oak_veneer_01", "2k", 1.2, rough_mul=0.9, norm=0.4, sat=0.9, val=1.0)
    tampo = mat("quartzo", (0.94, 0.94, 0.93), rough=0.12, coat=0.4)
    rod = mat("rodape_balcao", (0.12, 0.12, 0.13), rough=0.5)
    xc, yc = (x0 + x1) / 2, (y0 + y1) / 2
    box("balcao_rod", x1 - x0 - 0.06, y1 - y0 - 0.08, 0.10, (xc, yc + 0.02, 0), [rod])
    box("balcao", x1 - x0, y1 - y0, h - 0.14, (xc, yc, 0.10), [madeira, madeira], bevel=0.004)
    box("tampo", x1 - x0 + 0.06, y1 - y0 + 0.08, 0.04, (xc, yc, h - 0.04), [tampo], bevel=0.008, seg=3)

def pdv_caixa(x, y, z):
    preto = mat("eletron_preto", (0.02, 0.02, 0.025), rough=0.25, metal=0.2)
    tela = mat("tela", (0.03, 0.06, 0.10), rough=0.05, emit=0.6)
    branco = mat("eletron_branco", (0.9, 0.9, 0.9), rough=0.3)
    box("mon_base", 0.18, 0.14, 0.012, (x, y + 0.05, z), [preto], bevel=0.003)
    box("mon_haste", 0.04, 0.03, 0.22, (x, y + 0.07, z), [preto], bevel=0.004)
    m = box("monitor", 0.40, 0.025, 0.26, (x, y + 0.04, z + 0.16), [tela, preto], bevel=0.004)
    m.rotation_euler = (math.radians(8), 0, math.radians(192))
    box("impressora", 0.14, 0.18, 0.12, (x + 0.32, y + 0.02, z), [branco], bevel=0.015, seg=4)
    maq = box("maquininha", 0.075, 0.16, 0.02, (x - 0.35, y - 0.06, z), [preto], bevel=0.006, seg=3)
    maq.rotation_euler = (math.radians(12), 0, math.radians(-20))

def banco_moderno(x, y):
    madeira = mat_pbr("carvalho", "oak_veneer_01", "2k", 1.2, rough_mul=0.9, norm=0.4)
    preto = mat("ferro_preto", (0.03, 0.03, 0.035), rough=0.45, metal=0.8)
    for k in range(5): box("ripa", 1.3, 0.07, 0.03, (x, y - 0.17 + k * 0.085, 0.42), [madeira], bevel=0.006, seg=3)
    for sx in (-0.55, 0.55):
        box("perna", 0.04, 0.38, 0.03, (x + sx, y, 0.39), [preto]); box("perna2", 0.04, 0.03, 0.39, (x + sx, y - 0.17, 0), [preto]); box("perna3", 0.04, 0.03, 0.39, (x + sx, y + 0.17, 0), [preto])

def pessoa(x, y, h=1.70):
    m = mat("manequim", (0.13, 0.20, 0.33), rough=0.45, coat=0.3)
    cyl("pernas", 0.11, h * 0.47, (x, y, 0), [m]); cyl("tronco", 0.17, h * 0.33, (x, y, h * 0.47), [m], r2=0.15)
    me = bpy.data.meshes.new("cab"); bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=24, radius=0.105)
    bm.to_mesh(me); bm.free(); me.materials.append(m)
    for pg in me.polygons: pg.use_smooth = True
    ob = bpy.data.objects.new("cab", me); ob.location = (x, y, h - 0.105); link(ob)

# ================================================================ materiais de PDV
def wobbler(x, yf, z):
    acr = mat("haste_acr", (0.95, 0.97, 0.99), rough=0.03, transm=1.0, ior=1.49)
    box("wob_haste", 0.010, 0.11, 0.0025, (x, yf - 0.058, z), [acr])
    m = mat_img("wob", TEX + "arte_wobbler.png", cut=True, rough=0.25, coat=0.5)
    me = bpy.data.meshes.new("wob"); bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=True, radius=0.058, segments=64)
    for v in bm.verts: v.co = Vector((v.co.x, 0, v.co.y))
    uv = bm.loops.layers.uv.new()
    for f in bm.faces:
        for l in f.loops: l[uv].uv = (l.vert.co.x / 0.116 + 0.5, l.vert.co.z / 0.116 + 0.5)
    bm.to_mesh(me); bm.free(); me.materials.append(m)
    if me.polygons[0].normal.y > 0: me.flip_normals()
    ob = bpy.data.objects.new("wobbler", me); ob.location = (x, yf - 0.115, z - 0.01); ob.rotation_euler = (math.radians(-5), 0, math.radians(10))
    link(ob); s = ob.modifiers.new("s", "SOLIDIFY"); s.thickness = 0.0015

def stopper(x, yf, z):
    m = mat_img("stop", TEX + "arte_stopper.png", rough=0.3, coat=0.45)
    branco = mat("ps_borda", (0.95, 0.95, 0.95), rough=0.3)
    s = box("stopper", 0.003, 0.20, 0.30, (x, yf - 0.115, z), [branco, m, m])
    # projeta a arte nas duas faces laterais (normal ±X)
    me = s.data; me.materials.clear(); me.materials.append(branco); me.materials.append(mat_img("stop_lat", TEX + "arte_stopper.png", coord="GEN", rough=0.3, coat=0.45))
    nt = MATS["stop_lat"].node_tree; ti = [n for n in nt.nodes if n.type == "TEX_IMAGE"][0]
    tc = [n for n in nt.nodes if n.type == "TEX_COORD"][0]; sp = nt.nodes.new("ShaderNodeSeparateXYZ"); cb = nt.nodes.new("ShaderNodeCombineXYZ")
    # X da arte = 0,5 + (Y - 0,5) * sinal(normal X): cada face lateral mostra a arte sem espelhar
    geo = nt.nodes.new("ShaderNodeNewGeometry"); sn = nt.nodes.new("ShaderNodeSeparateXYZ")
    sg = nt.nodes.new("ShaderNodeMath"); sg.operation = "SIGN"
    sub = nt.nodes.new("ShaderNodeMath"); sub.operation = "SUBTRACT"; sub.inputs[1].default_value = 0.5
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
    add = nt.nodes.new("ShaderNodeMath"); add.operation = "ADD"; add.inputs[1].default_value = 0.5
    nt.links.new(geo.outputs["Normal"], sn.inputs[0]); nt.links.new(sn.outputs["X"], sg.inputs[0])
    nt.links.new(tc.outputs["Generated"], sp.inputs[0]); nt.links.new(sp.outputs["Y"], sub.inputs[0])
    nt.links.new(sub.outputs[0], mul.inputs[0]); nt.links.new(sg.outputs[0], mul.inputs[1]); nt.links.new(mul.outputs[0], add.inputs[0])
    nt.links.new(add.outputs[0], cb.inputs["X"]); nt.links.new(sp.outputs["Z"], cb.inputs["Y"]); nt.links.new(cb.outputs[0], ti.inputs["Vector"])
    for pg in me.polygons: pg.material_index = 1 if abs(pg.normal.x) > 0.9 else 0
    box("stop_clip", 0.012, 0.03, 0.05, (x, yf - 0.012, z + 0.12), [mat("clip", (0.85, 0.85, 0.85), rough=0.3)], bevel=0.003)

def testeira(g):
    m = mat_img("test", TEX + "arte_testeira.png", coord="FRONT", rough=0.3, emit=0.35)
    borda = mat("test_borda", (0.04, 0.05, 0.07), rough=0.35, metal=0.5)
    box("testeira", g["W"] + 0.04, 0.06, 0.32, (g["x0"] + g["W"] / 2, g["yb"] - 0.05, g["H"] + 0.02), [m, borda], bevel=0.004)

def clip_strip(x, y, z_top, n=4):
    tira = mat("tira", (0.93, 0.96, 0.98), rough=0.05, transm=0.9, ior=1.45)
    box("tira", 0.004, 0.035, 0.66, (x - 0.002, y, z_top - 0.66), [tira])
    plane("clip_cab", 0.12, 0.09, (x - 0.006, y, z_top - 0.02), mat_img("clipcab", TEX + "arte_clipstrip.png", rough=0.3, coat=0.4), rot=(0, 0, -math.pi / 2))
    for k in range(n):
        ob = caixa_ouro("banni3_a" if k % 2 == 0 else "banni3_b", x - 0.016, y, z_top - 0.17 - k * 0.135)
        ob.rotation_euler = (0, 0, -math.pi / 2)

def display_balcao(x, y, z):
    pap = mat("pap_td", (0.80, 0.27, 0.34), rough=0.55)
    box("bandeja", 0.30, 0.20, 0.07, (x, y, z), [pap], bevel=0.003)
    for r in range(2):
        for c in range(2): caixa_ouro(["topdog_a", "topdog_b"][c], x - 0.075 + c * 0.15, y - 0.05 + r * 0.06, z + 0.02)
    plane("cab_balcao", 0.30, 0.17, (x, y + 0.09, z + 0.07), mat_img("bal", TEX + "arte_balcao.png", rough=0.3, coat=0.4), rot=(math.radians(-10), 0, 0))

def take_one(x, y, z):
    acr = mat("to_acr", (0.94, 0.97, 0.99), rough=0.02, transm=1.0, ior=1.49)
    box("to_base", 0.17, 0.09, 0.006, (x, y, z), [acr]); box("to_fundo", 0.17, 0.005, 0.23, (x, y + 0.04, z), [acr])
    box("to_frente", 0.17, 0.005, 0.07, (x, y - 0.035, z), [acr])
    for k in range(3):
        plane(f"fol{k}", 0.14, 0.198, (x, y + 0.03 - k * 0.012, z + 0.008), mat_img("folheto", TEX + "arte_takeone.png", rough=0.4), rot=(math.radians(-9), 0, 0))

def display_chao(x, y):
    lat = mat_img("dc_lat", TEX + "arte_displaychao_lat.png", coord="GEN", rough=0.5)
    pap = mat("papelao_v", (0.06, 0.45, 0.19), rough=0.55)
    W, D, H = 0.52, 0.40, 1.30
    for sx in (x - W / 2, x + W / 2): box("dc_lado", 0.012, D, H, (sx, y, 0), [lat, lat], bevel=0.002)
    box("dc_fundo", W, 0.012, H, (x, y + D / 2, 0), [pap])
    for k, z in enumerate((0.06, 0.48, 0.90)):
        box(f"dc_pr{k}", W, D, 0.02, (x, y, z - 0.02), [pap], bevel=0.002)
        box(f"dc_frente{k}", W, 0.01, 0.06, (x, y - D / 2, z - 0.06), [pap])
        fill([("h3", "herbalvet", 3)], x - W / 2 + 0.01, x + W / 2, z, y - D / 2, deep=1, gap=0.025)
    box("dc_cab", W + 0.04, 0.02, 0.40, (x, y - D / 2 + 0.03, H), [mat_img("dc_cab", TEX + "arte_displaychao.png", coord="FRONT", rough=0.3, coat=0.35), pap])

def ilha(x, y, erro=False):
    art = "arte_cubo_wellpet.png" if erro else "arte_ilha.png"
    m = mat_img("cubo_" + ("e" if erro else "o"), TEX + art, coord="GEN", proj="BOX", rough=0.4, coat=0.3)
    s = 0.40
    for i in range(2):
        for j in range(2):
            box(f"cubo{i}{j}", s, s, s, (x - s / 2 + i * s, y - s / 2 + j * s, 0), [m, m, mat("cubo_topo", (0.96, 0.96, 0.95), rough=0.4)], bevel=0.003)
    tampo = mat("ilha_tampo", (0.96, 0.96, 0.95), rough=0.35)
    box("ilha_tampo", 0.84, 0.84, 0.012, (x, y, s), [tampo], bevel=0.003)
    fill([("h3", "herbalvet", 3)], x - 0.40, x + 0.40, s + 0.012, y - 0.36, deep=1, gap=0.03)
    fill([("h3", "enziclim", 5)] if not erro else [("h3", "herbalvet", 3)], x - 0.40, x + 0.40, s + 0.012, y + 0.04, deep=1, gap=0.035)

def cartaz(x, y, z):
    box("moldura", 0.63, 0.02, 0.88, (x, y + 0.006, z - 0.02), [mat("moldura", (0.10, 0.11, 0.12), rough=0.3, metal=0.6)], bevel=0.004)
    plane("cartaz", 0.594, 0.841, (x, y - 0.006, z), mat_img("cartaz", TEX + "arte_cartaz.png", rough=0.35))
    box("cartaz_vidro", 0.60, 0.003, 0.85, (x, y - 0.010, z - 0.004), [mat_vidro("vidro_cartaz")])

def adesivo(x, y, rz):
    m = mat_img("ades", TEX + "arte_adesivo.png", cut=True, rough=0.3, coat=0.3)
    me = bpy.data.meshes.new("ades"); s = 0.31
    me.from_pydata([(-s, -s, 0), (s, -s, 0), (s, s, 0), (-s, s, 0)], [], [(0, 1, 2, 3)]); me.update()
    uv = me.uv_layers.new()
    for i, c in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]): uv.data[i].uv = c
    me.materials.append(m); ob = bpy.data.objects.new("ades", me); ob.location = (x, y, 0.0015); ob.rotation_euler = (0, 0, rz); link(ob)

# ================================================================ cena
def construir(v):
    global rng; rng = random.Random(11)
    casca(v); R = {}
    # ---------------- FARMÁCIA (estante atrás do balcão), 2 módulos, 7 níveis, fita de LED
    lv = [0.15, 0.42, 0.69, 0.96, 1.23, 1.50, 1.77]
    g = gondola("farm", 0.6, 2, 1.0, 3.62, 0.35, 2.05, lv, led=True, rail_art={(3, 0): True} if v.get("regua") else None)
    R["farm"] = g; yf = g["yf"]
    if v.get("testeira", True): testeira(g)
    antes = v.get("estado") == "antes"
    messy = {"falha": 0.34, "giro": 0.38, "recuo": 0.45, "caido": 0.24} if antes else None
    a1, b1, a2, b2, fim = 0.6, 1.1, 1.6, 2.1, 2.6
    G = lambda nm, w, h: ("gen", (nm, (w, 0.03, h)))
    c_anti = [G("anti_laranja", 0.08, 0.12), G("anti_azul", 0.08, 0.12), G("anti_roxo", 0.072, 0.108), G("anti_vinho", 0.08, 0.12)]
    c_verm = [G("verm_amarelo", 0.12, 0.072), G("verm_azul", 0.12, 0.072)]
    potes = [("jar", ("pote_articula", 0.042, 0.115)), ("jar", ("pote_vitamina", 0.042, 0.115)), ("jar", ("pote_pelo", 0.038, 0.10))]
    meds = [G("med_cinza", 0.075, 0.10), G("med_verde", 0.075, 0.10), G("med_petroleo", 0.075, 0.10)]
    Wb = lambda *k: [("box", x) for x in k]
    plano = {
        6: [(Wb("leevre_a", "leevre_b"), a1, b1), (c_anti, b1, a2), ([("h3", "plenipil")], a2, b2), (potes, b2, fim)],
        5: [(Wb("wellpet_a", "wellpet_b", "wellpet_c", "wellpet_d", "wellpet_e", "banni3_a", "banni3_b"), a1, b1), (c_anti, b1, a2), (Wb("topdog_a", "topdog_b", "topdog_c"), a2, b2), (c_verm, b2, fim)],
        4: [(Wb("leevre_a", "leevre_b", "wellpet_d", "wellpet_e"), a1, b1), (c_anti, b1, a2), (Wb("topdog_a", "topdog_b", "topdog_c"), a2, b2), (c_verm, b2, fim)],
        3: [(Wb("banni3_a", "banni3_b"), a1, b1), (c_anti, b1, a2), ([("h3", "plenipil")], a2, b2), (potes, b2, fim)],
        2: [(Wb("wellpet_a", "wellpet_b", "wellpet_c"), a1, b1), (c_anti, b1, a2), (potes, a2, b2), (potes, b2, fim)],
        1: [(c_anti, a1, b1), (meds, b1, a2), (meds, a2, b2), (meds, b2, fim)],
        0: [(meds, a1, b1), (meds, b1, a2), (meds, a2, b2), (meds, b2, fim)],
    }
    if antes:
        plano[5][0] = ([("box", "wellpet_a"), c_anti[0], ("box", "wellpet_c"), ("box", "banni3_a"), c_anti[2], ("box", "wellpet_b")], a1, b1)
        plano[4][2] = ([("box", "topdog_a"), ("box", "wellpet_e"), ("box", "topdog_c"), ("box", "leevre_a")], a2, b2)
        plano[3][0] = ([("box", "banni3_b"), ("box", "wellpet_d"), c_anti[1]], a1, b1)
    for lvl, segs in plano.items():
        xs = []
        for items, a, b in segs:
            seen = set()
            for cx, w, it in fill(items, a, b, lv[lvl], yf, deep=2, messy=messy):
                k = (it[0], str(it[1]))
                if k not in seen: seen.add(k); xs.append(cx)
        price_tags(g, lvl, xs if not antes else [x for x in xs if rng.random() < 0.25], seed=lvl * 3)
    R["farm_blocos"] = {"antipulga": (0.85, yf, 1.62), "concorrente": (1.35, yf, 1.62), "vermifugo": (1.85, yf, 1.62), "suplementos": (1.85, yf, 1.06), "concorrente2": (2.35, yf, 1.62)}
    if v.get("wobbler_farm"): wobbler(0.74, yf, 1.53)
    if v.get("clip"): clip_strip(0.6 - 0.03, 3.43, 1.50)
    if v.get("zonas"):
        for nm, z0, z1, c in (("pes", 0.0, 0.8, (0.55, 0.58, 0.62)), ("maos", 0.8, 1.2, (0.0, 0.49, 0.76)), ("olhos", 1.2, 1.6, (0.06, 0.68, 0.19))):
            plane("zona_" + nm, 1.02, z1 - z0, (1.1, yf - 0.035, z0), mat("zona_" + nm, c, rough=1.0, alpha=0.22))
        pessoa(0.22, yf - 0.32)
    texto("Farmácia", 0.24, (1.6, 3.62, 2.72), mat("letras", (1, 1, 1), rough=0.35, emit=1.2), ext=0.02)
    # cartaz, banco, relógio, plantas (área de espera)
    cartaz(3.25, 3.625, 1.35); banco_moderno(3.2, 3.36)
    importar("wall_clock", (3.25, 3.62, 2.55), rz=0.0)
    importar("potted_plant_01", (3.85, 3.35, 0), rz=0.6)
    # ---------------- BALCÃO / CAIXA
    if v.get("balcao", True):
        balcao(0.5, 2.7, 1.9, 2.5)
        pdv_caixa(1.75, 2.22, 1.0)
        if v.get("display_balcao", True): display_balcao(0.95, 2.10, 1.0)
        if v.get("takeone", True): take_one(2.42, 2.12, 1.0)
        importar("calathea_orbifolia_01", (2.62, 2.40, 1.0), keep=["_a"], escala=0.75)
        importar("metal_stool_01", (2.2, 2.95, 0), rz=0.4)
        for k, (px, py, pz) in enumerate(((0.80, 2.92, 0), (0.80, 2.92, 0.34), (1.25, 2.95, 0))):
            importar("cardboard_box_01", (px, py, pz), rz=math.radians(90) + 0.08 * k)
        for px in (0.82, 2.38):
            lm = importar("modern_ceiling_lamp_01", (px, 2.05, 3.2), top=True, escala=0.7)
            L = bpy.data.lights.new("globo", "POINT"); L.energy = 35; L.shadow_soft_size = 0.12; L.color = (1.0, 0.86, 0.66)
            o = bpy.data.objects.new("globo", L); o.location = (px, 2.05, 2.62); link(o)
    # ---------------- HIGIENE DO AMBIENTE
    lh = [0.15, 0.55, 0.95, 1.35]
    h = gondola("hig", -2.6, 2, 1.0, 3.62, 0.42, 1.8, lh, led=False)
    R["hig"] = h; yh = h["yf"]
    tapete = ("gen", ("tapete", (0.30, 0.12, 0.20)), 3); areia = ("bag", ("areia", (0.25, 0.12, 0.34)), 3)
    desinf = [("frasco", ("desinf_azul", 0.05, 0.25), 3), ("frasco", ("desinf_lilas", 0.045, 0.22), 3)]
    fill([tapete], -2.6, -1.6, lh[0], yh); fill([areia], -1.6, -0.6, lh[0], yh, gap=0.02)
    fill([tapete], -2.6, -1.6, lh[1], yh); fill([areia], -1.6, -0.6, lh[1], yh, gap=0.02)
    fill(desinf, -2.6, -1.6, lh[2], yh)
    buraco = v.get("extra") == "errado"
    herb = [] if buraco else [("h3", "herbalvet", 4)]
    fill(herb + [("h3", "enziclim", 3)], -1.6 + (0.62 if buraco else 0), -0.6, lh[2], yh, deep=1, gap=0.025, repeat=False)
    fill([("h3", "enziclim", 6)], -1.6, -0.6, lh[3], yh, deep=1, gap=0.03)
    fill(desinf, -2.6, -1.6, lh[3], yh)
    price_tags(h, 2, [-1.5, -1.25, -0.9, -0.7] if not buraco else [-0.9, -0.7], seed=5); price_tags(h, 3, [-1.5, -1.1, -0.8], seed=6)
    R["hig_buraco"] = (-1.3, yh, lh[2] + 0.13)
    if v.get("stopper"): stopper(-1.62, yh, 1.42)
    if v.get("extra") in ("certo", "errado") or v.get("display_chao"):
        display_chao(-0.22, yh - 0.05); R["display"] = (-0.22, yh - 0.25, 1.0)
    placa_suspensa("Higiene e ambiente", -1.6, 2.75, larg=1.6)
    # ---------------- RAÇÃO
    lr = [0.15, 0.64, 1.13]
    r = gondola("rac", -2.75, 1, 1.5, 1.15, 0.45, 1.6, lr, peg=False)
    s1 = [("bag", ("racao_adulto", (0.32, 0.13, 0.44)), 2), ("bag", ("racao_filhote", (0.32, 0.13, 0.44)), 2)]
    s2 = [("bag", ("racao_pele", (0.30, 0.13, 0.42)), 2), ("bag", ("racao_gato", (0.26, 0.11, 0.36)), 2)]
    for k, z in enumerate(lr): fill(s1 if k % 2 == 0 else s2, -2.75, -1.25, z, r["yf"], deep=2, gap=0.03)
    if v.get("wobbler_racao"): wobbler(-1.78, r["yf"], 1.56)
    if v.get("stopper_racao"): stopper(-1.25, r["yf"], 1.22)
    placa_suspensa("Rações", -2.0, 0.92, larg=1.0)
    R["rac"] = r
    # ---------------- ILHA, ADESIVO, PLANTAS, SPOTS
    if v.get("ilha"): ilha(-0.55, 1.55, erro=v["ilha"] == "erro"); R["ilha"] = (-0.55, 1.55, 0.6)
    if v.get("adesivo"): adesivo(-0.25, 0.65, math.radians(-38))
    importar("pachira_aquatica_01", (-3.55, 2.95, 0.42), keep=["_d"], escala=0.95)
    vaso = mat("vaso", (0.15, 0.15, 0.16), rough=0.6); cyl("vaso_pachira", 0.24, 0.42, (-3.55, 2.95, 0), [vaso, vaso], r2=0.2)
    importar("potted_plant_02", (-3.55, -0.9, 0), rz=1.2)
    if v.get("teto", True):
        trilho_spots([((1.0, 2.55, 3.2), (0.9, 3.4, 1.2)), ((2.2, 2.55, 3.2), (2.2, 3.4, 1.2)),
                      ((-2.1, 2.55, 3.2), (-2.1, 3.4, 0.9)), ((-1.1, 2.55, 3.2), (-1.1, 3.4, 0.9)),
                      ((-2.0, -0.2, 3.2), (-2.0, 0.9, 0.8)), ((3.25, 2.6, 3.2), (3.25, 3.62, 1.7)),
                      ((-0.55, 0.9, 3.2), (-0.55, 1.55, 0.45))])
        importar("security_camera_01", (3.85, 3.5, 3.2), rz=math.radians(-135), top=True)
    return R

def camera(loc, target, lens=35, res=(1800, 1200), fstop=None):
    sc = bpy.context.scene; cam = bpy.data.cameras.new("cam"); cam.lens = lens; cam.sensor_width = 36
    ob = bpy.data.objects.new("cam", cam); link(ob); ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    if fstop:
        cam.dof.use_dof = True; cam.dof.focus_distance = (Vector(target) - Vector(loc)).length; cam.dof.aperture_fstop = fstop
    sc.camera = ob; sc.render.resolution_x = int(res[0] * SCALE); sc.render.resolution_y = int(res[1] * SCALE)
    sc.render.resolution_percentage = 100; return ob

# shot: (variantes, câmera, alvo, lente, resolução, f-stop)
SH = {
    "F-DEPOIS":        ({"estado": "ok", "balcao": False}, (1.1, 1.22, 1.05), (1.1, 3.4, 0.98), 35, (1500, 2000), 9),
    "F-ANTES":         ({"estado": "antes", "balcao": False}, (1.1, 1.22, 1.05), (1.1, 3.4, 0.98), 35, (1500, 2000), 9),
    "F-GONDOLA-ZONAS": ({"estado": "ok", "balcao": False, "zonas": True}, (0.85, 0.98, 1.08), (0.95, 3.4, 0.98), 32, (1600, 1800), 11),
    "F-PRATELEIRA-IDEAL": ({"estado": "ok", "balcao": False}, (1.6, 0.70, 1.2), (1.6, 3.4, 1.14), 35, (1800, 1800), 11),
    "F-MAT-WOBBLER":   ({"estado": "ok", "balcao": False, "wobbler_farm": True}, (1.0, 2.42, 1.66), (0.76, 3.26, 1.52), 55, (1800, 1300), 3.2),
    "F-MAT-REGUA":     ({"estado": "ok", "balcao": False, "regua": True}, (1.08, 2.50, 1.10), (0.95, 3.3, 0.94), 50, (1800, 1250), 3.5),
    "F-MAT-TESTEIRA":  ({"estado": "ok"}, (1.6, -0.45, 1.62), (1.6, 3.3, 1.62), 32, (2000, 1330), 10),
    "F-MAT-CLIPSTRIP": ({"estado": "ok", "clip": True}, (-0.15, 2.78, 1.30), (0.56, 3.43, 1.16), 45, (1500, 1650), 4),
    "F-MAT-DISPLAY-BALCAO": ({"estado": "ok"}, (0.78, 1.18, 1.40), (0.97, 2.12, 1.10), 50, (1800, 1300), 3.2),
    "F-MAT-TAKEONE":   ({"estado": "ok"}, (2.62, 1.36, 1.34), (2.42, 2.14, 1.10), 55, (1600, 1300), 3.2),
    "F-MAT-CARTAZ":    ({"estado": "ok"}, (2.55, 1.15, 1.30), (3.25, 3.5, 1.15), 32, (1500, 1650), 8),
    "F-PONTO-EXTRA-CERTO":  ({"estado": "ok", "extra": "certo"}, (0.8, 1.32, 1.58), (-1.0, 3.2, 0.98), 28, (2000, 1400), 8),
    "F-PONTO-EXTRA-ERRADO": ({"estado": "ok", "extra": "errado"}, (0.8, 1.32, 1.58), (-1.0, 3.2, 0.98), 28, (2000, 1400), 8),
    "F-MAT-DISPLAY-CHAO": ({"estado": "ok", "display_chao": True}, (0.42, 1.42, 1.42), (-0.22, 3.05, 1.04), 33, (1500, 1650), 6),
    "F-MAT-STOPPER":   ({"estado": "ok", "stopper": True}, (-0.30, 2.42, 1.52), (-1.62, 3.08, 1.44), 45, (1800, 1300), 3.5),
    "F-MAT-ILHA":      ({"estado": "ok", "ilha": "ok"}, (1.30, 0.30, 1.50), (-0.45, 1.62, 0.42), 35, (1800, 1300), 7),
    "F-ERRO-CARNAVAL": ({"estado": "ok", "ilha": "erro"}, (1.30, 0.30, 1.50), (-0.45, 1.62, 0.42), 35, (1800, 1300), 7),
    "F-MAT-ADESIVO-CHAO": ({"estado": "ok", "adesivo": True}, (0.38, -0.30, 1.78), (-0.25, 0.75, 0.0), 35, (1800, 1300), 6),
    "F-CROSS-MERCH":   ({"estado": "ok", "wobbler_racao": True}, (-1.12, -0.42, 1.56), (-1.80, 0.62, 1.36), 42, (1800, 1300), 3.2),
    "F-LOJA":          ({"estado": "ok", "ilha": "ok", "adesivo": True, "display_chao": True, "wobbler_racao": True}, (3.4, -2.6, 2.9), (-0.4, 2.0, 0.6), 22, (2200, 1380), 14),
    "F-CAPA":          ({"estado": "ok", "ilha": "ok", "display_chao": True}, (-1.2, -0.6, 1.25), (1.2, 3.0, 1.05), 30, (2200, 1400), 5),
    # aberturas de capítulo (panorâmicas 21:9)
    "O-ENTRADA":  ({"estado": "ok", "ilha": "ok", "display_chao": True, "wobbler_racao": True, "adesivo": True}, (-3.55, -2.55, 1.62), (1.4, 2.9, 1.0), 22, (2400, 1030), 12),
    "O-BALCAO":   ({"estado": "ok", "ilha": "ok"}, (0.62, 0.85, 1.30), (1.75, 3.5, 1.32), 30, (2400, 1030), 4),
    "O-CORREDOR": ({"estado": "ok", "wobbler_racao": True, "stopper": True, "display_chao": True}, (-0.35, -2.2, 1.58), (-2.5, 2.6, 0.95), 26, (2400, 1030), 9),
    "O-MACRO":    ({"estado": "ok", "balcao": False, "wobbler_farm": True}, (1.42, 2.78, 1.42), (0.90, 3.45, 1.32), 60, (2400, 1030), 2.4),
    "O-ALTO":     ({"estado": "ok", "ilha": "ok", "display_chao": True, "wobbler_racao": True, "adesivo": True, "stopper": True}, (0.2, -3.1, 2.75), (-0.6, 2.2, 0.6), 20, (2400, 1030), 14),
    "O-FARMACIA": ({"estado": "ok", "ilha": "ok"}, (3.3, 0.9, 1.5), (0.9, 3.4, 1.2), 30, (2400, 1030), 5),
    "O-RACAO":    ({"estado": "ok", "wobbler_racao": True, "stopper_racao": True, "ilha": "ok"}, (-3.3, -1.3, 1.45), (0.9, 3.1, 1.1), 24, (2400, 1030), 8),
}

def anchors(shot, R):
    a = {}
    if shot == "F-GONDOLA-ZONAS":
        g = R["farm"]
        for nm, z in (("pes_meio", 0.4), ("maos_meio", 1.0), ("olhos_meio", 1.4), ("lim_080", 0.8), ("lim_120", 1.2), ("lim_160", 1.6)):
            a[nm] = (1.62, g["yf"] - 0.035, z)
    if shot in ("F-PRATELEIRA-IDEAL", "F-DEPOIS", "F-ANTES"):
        for k, p in R["farm_blocos"].items(): a[k] = p
    if shot.startswith("F-PONTO-EXTRA"): a["buraco"] = R["hig_buraco"]; a["display"] = R.get("display")
    return {k: v for k, v in a.items() if v}

def render(shot):
    v, loc, tgt, lens, res, fs = SH[shot]
    sc = reset(); R = construir(v); cam = camera(loc, tgt, lens, res, fs)
    sc.render.filepath = OUT + shot + ".png"; bpy.ops.render.render(write_still=True)
    pts = {k: [round(p.x * 100, 2), round((1 - p.y) * 100, 2)] for k, co in anchors(shot, R).items() for p in [world_to_camera_view(sc, cam, Vector(co))]}
    f = OUT + "anot.json"; data = json.load(open(f)) if os.path.exists(f) else {}
    data[shot] = pts; json.dump(data, open(f, "w"), indent=1); print("RENDERIZADO", shot)

for s in SHOTS:
    if s in SH: render(s)
    else: print("SHOT DESCONHECIDO", s)
