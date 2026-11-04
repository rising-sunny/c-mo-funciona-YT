"""CLI:  python -m mech render bench_vise --preset draft   |  stills | compose | setup"""
import argparse, importlib, json, os, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BLENDER = os.environ.get("BLENDER", "/opt/blender/blender")


def run_blender(ep, preset, out, extra):
    cmd = ["xvfb-run", "-a", BLENDER, "-b", "-P", os.path.join(ROOT, "mech/blender/entry.py"), "--",
           "--episode", ep, "--preset", preset, "--out", out] + extra
    subprocess.run(cmd, check=True, cwd=ROOT)


def main():
    ap = argparse.ArgumentParser(prog="mech")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("setup")
    pf = sub.add_parser("final")
    pf.add_argument("episode")
    pf.add_argument("--preset", default="final")
    pf.add_argument("--seconds", type=float, default=None)
    pn = sub.add_parser("narrate")
    pn.add_argument("episode")
    pn.add_argument("--voice", default="am_puck")
    pn.add_argument("--speed", type=float, default=1.05)
    for name in ("render", "compose", "stills"):
        p = sub.add_parser(name)
        p.add_argument("episode")
        p.add_argument("--preset", default="draft")
        p.add_argument("--frames", default=None)
        p.add_argument("--only", default=None)
        p.add_argument("--no-render", action="store_true")
        p.add_argument("--seconds", type=float, default=None, help="limita la duración (muestras cortas)")
    a = ap.parse_args()
    if a.cmd == "setup":
        sys.exit(subprocess.call([os.path.join(ROOT, "scripts/setup_env.sh")]))

    sys.path.insert(0, ROOT)
    from mech.presets import PRESETS
    if a.cmd == "final":
        from mech import final
        spec = importlib.import_module(f"episodes.{a.episode}.spec")
        pr = PRESETS[a.preset]
        d = os.path.join(ROOT, "out", a.episode, a.preset, "ui60")
        if not os.path.exists(os.path.join(d, "ui.json")):
            run_blender(a.episode, a.preset, d, ["--labels-only", "--ui-fps", str(pr.get("out_fps", pr["fps"]))])
        print("vídeo:", final.build(spec, a.episode, ROOT, a.preset, a.seconds))
        return
    if a.cmd == "narrate":
        from mech import narration
        spec = importlib.import_module(f"episodes.{a.episode}.spec")
        narration.build(spec, os.path.join(ROOT, "out", a.episode, "audio"), a.voice, a.speed)
        return
    from mech.compose import Composer, encode
    spec = importlib.import_module(f"episodes.{a.episode}.spec")
    pr = PRESETS[a.preset]
    base = os.path.join(ROOT, "out", a.episode, a.preset)
    comp = Composer(spec, a.preset)

    if a.cmd == "stills":
        d = os.path.join(base, "stills")
        if not a.no_render:
            run_blender(a.episode, a.preset, d, ["--stills"] + (["--only", a.only] if a.only else []))
        ui = json.load(open(os.path.join(d, "ui.json")))
        for i, s in enumerate(spec.SCENES):
            n = f"s{i}"
            if n in ui and os.path.exists(os.path.join(d, n + ".png")):
                t = spec.scene_start(i) + 0.8 * s["dur"]
                comp.frame(t, os.path.join(d, n + ".png"), ui[n]).save(os.path.join(d, f"composed_{n}.png"))
        print("stills en", d)
        return

    d = os.path.join(base, "frames")
    if a.cmd == "render" and not a.no_render:
        run_blender(a.episode, a.preset, d, (["--frames", a.frames] if a.frames else ([f"--frames", f"0:{int(a.seconds * pr['fps'])}"] if a.seconds else [])))
    ui = json.load(open(os.path.join(d, "ui.json")))
    total = int(round((a.seconds or spec.total_duration()) * pr["fps"]))
    out = os.path.join(base, f"{a.episode}_{a.preset}.mp4")

    def frames():
        for i in range(total):
            n = f"f_{i:05d}"
            p = os.path.join(d, n + ".png")
            if os.path.exists(p):
                yield comp.frame(i / pr["fps"], p, ui.get(n, []))
    encode(frames(), out, pr["fps"], (comp.W, comp.H))
    print("vídeo:", out)


if __name__ == "__main__":
    main()
