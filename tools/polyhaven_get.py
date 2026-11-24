"""Baixa assets CC0 do Poly Haven com todas as dependências (texturas), preservando caminhos relativos.
Uso: python3 tools/polyhaven_get.py <destino> <tipo:id:res> ...
  tipo = model (gltf), texture (blend+maps), hdri (exr)
Ex.: python3 tools/polyhaven_get.py "/Volumes/.../ourofino-3d" model:CashRegister_01:1k hdri:crosswalk:2k texture:grey_tiles:2k
"""
import json, os, sys, urllib.request

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "ourofino-guide-build"})
    with urllib.request.urlopen(req, timeout=120) as r: return r.read()

def save(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 0: return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "wb").write(get(url))

dest = sys.argv[1]
for spec in sys.argv[2:]:
    kind, aid, res = spec.split(":")
    files = json.loads(get(f"https://api.polyhaven.com/files/{aid}"))
    base = os.path.join(dest, kind, aid)
    if kind == "model":
        g = files["gltf"][res]["gltf"]
        save(g["url"], os.path.join(base, os.path.basename(g["url"])))
        for rel, inf in g.get("include", {}).items(): save(inf["url"], os.path.join(base, rel))
    elif kind == "hdri":
        h = files["hdri"][res]["exr"]; save(h["url"], os.path.join(base, f"{aid}_{res}.exr"))
    elif kind == "texture":
        for mapname in ("Diffuse", "nor_gl", "Rough", "Displacement", "AO", "arm"):
            if mapname in files and res in files[mapname]:
                fmt = "jpg" if "jpg" in files[mapname][res] else list(files[mapname][res])[0]
                u = files[mapname][res][fmt]["url"]; save(u, os.path.join(base, os.path.basename(u)))
    print("ok", spec)
