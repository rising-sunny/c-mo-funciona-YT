"""Punto de entrada dentro de Blender:
blender -b -P mech/blender/entry.py -- --episode bench_vise --preset draft --out DIR [--frames A:B | --stills]
"""
import argparse, importlib, json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

import bpy  # noqa: E402
from mech.blender import kit  # noqa: E402
from mech.presets import PRESETS  # noqa: E402


def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    ap = argparse.ArgumentParser()
    ap.add_argument("--episode", required=True)
    ap.add_argument("--preset", default="draft")
    ap.add_argument("--out", required=True)
    ap.add_argument("--frames", default=None, help="A:B (índices de fotograma, B excluido)")
    ap.add_argument("--only", default=None, help="stills: lista separada por comas, p.ej. s1,s4")
    ap.add_argument("--labels-only", action="store_true", help="solo calcula etiquetas 2D (sin render)")
    ap.add_argument("--ui-fps", type=int, default=60)
    ap.add_argument("--stills", action="store_true", help="un fotograma por escena para revisar")
    a = ap.parse_args(argv)

    pr = PRESETS[a.preset]
    spec = importlib.import_module(f"episodes.{a.episode}.spec")
    scn = importlib.import_module(f"episodes.{a.episode}.scene")

    scene = kit.clear_scene()
    cam = kit.setup_stage(scene, pr["w"], pr["h"], pr["samples"], pr["fps"], pr.get("bounces", 6))
    model = scn.Vise()
    model.build(scene, cam)

    fps = a.ui_fps if a.labels_only else pr["fps"]
    total = int(round(spec.total_duration() * fps))
    if a.labels_only:
        os.makedirs(a.out, exist_ok=True)
        ui = {f"f_{i:05d}": model.apply(i / fps) for i in range(total)}
        json.dump(ui, open(os.path.join(a.out, "ui.json"), "w"))
        print("LABELS", len(ui), flush=True)
        return
    if a.stills:
        times = {f"s{i}": spec.scene_start(i) + 0.8 * s["dur"] for i, s in enumerate(spec.SCENES)}
        jobs = [(n, t) for n, t in times.items() if not a.only or n in a.only.split(",")]
    else:
        lo, hi = (0, total) if not a.frames else map(int, a.frames.split(":"))
        jobs = [(f"f_{i:05d}", i / fps) for i in range(lo, min(hi, total))]

    os.makedirs(a.out, exist_ok=True)
    ui = {}
    ui_path = os.path.join(a.out, "ui.json")
    if os.path.exists(ui_path):
        ui = json.load(open(ui_path))
    for name, t in jobs:
        path = os.path.join(a.out, name + ".png")
        labels = model.apply(t)
        ui[name] = labels
        if os.path.exists(path) and not a.stills:   # reanudar solo en vídeo; los estáticos siempre se regeneran
            continue
        scene.render.filepath = path
        bpy.ops.render.render(write_still=True)
        print(f"RENDERED {name} t={t:.2f}", flush=True)
        json.dump(ui, open(ui_path, "w"))
    json.dump(ui, open(ui_path, "w"))
    json.dump(dict(fps=fps, total=total, w=pr["w"], h=pr["h"]), open(os.path.join(a.out, "meta.json"), "w"))


main()
