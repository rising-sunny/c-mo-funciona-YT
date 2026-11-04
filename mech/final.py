"""Ensamblado final: 3D (30 fps) -> interpolación a 60 fps -> texto/subtítulos/etiquetas a 60 fps -> audio -> MP4."""
import json, os, subprocess, sys
from PIL import Image
from mech import audio
from mech.compose import Composer
from mech.presets import PRESETS


def build(spec, episode, root, preset="final", seconds=None):
    pr = PRESETS[preset]
    in_fps, out_fps = pr["fps"], pr.get("out_fps", pr["fps"])
    base = os.path.join(root, "out", episode)
    frames = os.path.join(base, preset, "frames")
    ui_path = os.path.join(base, preset, "ui60", "ui.json")
    total = seconds or spec.total_duration()
    n_in, n_out = int(round(total * in_fps)), int(round(total * out_fps))
    missing = [i for i in range(n_in) if not os.path.exists(os.path.join(frames, f"f_{i:05d}.png"))]
    if missing:
        sys.exit(f"faltan {len(missing)} fotogramas 3D (primero: {missing[0]}); termina el render")
    if not os.path.exists(ui_path):
        sys.exit("faltan etiquetas a 60 fps: ejecuta el pase --labels-only")
    ui = json.load(open(ui_path))

    wav = audio.mix(spec, os.path.join(base, "audio"), os.path.join(base, "mix.wav"))
    comp = Composer(spec, preset)
    rw, rh = pr["w"], pr["h"]
    bg = comp.bg.crop((0, comp.region[1], comp.W, comp.region[1] + round(rh * comp.W / rw))).convert("RGB").resize((rw, rh), Image.LANCZOS)
    bg_path = os.path.join(base, preset, "region_bg.png")
    bg.save(bg_path)

    interp = subprocess.Popen(
        ["ffmpeg", "-loglevel", "error", "-loop", "1", "-framerate", str(in_fps), "-i", bg_path,
         "-framerate", str(in_fps), "-i", os.path.join(frames, "f_%05d.png"),
         "-filter_complex",
         f"[0:v][1:v]overlay=shortest=1:format=auto,format=rgb24,"
         f"minterpolate=fps={out_fps}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1",
         "-frames:v", str(n_out + 4), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        stdout=subprocess.PIPE)
    out_path = os.path.join(base, f"{episode}_short.mp4")
    enc = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{comp.W}x{comp.H}",
         "-r", str(out_fps), "-i", "-", "-i", wav, "-map", "0:v", "-map", "1:a",
         "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(out_fps),
         "-af", "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000", "-c:a", "aac", "-b:a", "192k",
         "-t", f"{total:.3f}", "-movflags", "+faststart", out_path],
        stdin=subprocess.PIPE)
    size, last = rw * rh * 3, None
    for j in range(n_out):
        buf = interp.stdout.read(size)
        if len(buf) == size:
            last = Image.frombytes("RGB", (rw, rh), buf)
        if last is None:
            break
        im = comp.compose(j / out_fps, last, ui.get(f"f_{j:05d}", []))
        enc.stdin.write(im.tobytes())
        if j % 300 == 0:
            print(f"  {j}/{n_out}", flush=True)
    interp.stdout.close()
    interp.kill()
    enc.stdin.close()
    enc.wait()
    return out_path
