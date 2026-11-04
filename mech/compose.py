"""Compositor 2D (PIL): fondo, render 3D, tipografía, ecuaciones, etiquetas ancladas, barra de progreso."""
import importlib, json, os, subprocess
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageFilter
from mech.blender.palette import COL
from mech.presets import PRESETS, REGION_Y

FONT_DIR = "/usr/share/fonts/opentype/inter/"
BASE = (1080, 1920)


def font(weight, size):
    for path in (FONT_DIR + f"Inter-{weight}.otf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def smooth(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def spaced(draw, xy, text, fnt, fill, spacing=5, anchor_center=False):
    w = sum(draw.textlength(c, font=fnt) + spacing for c in text) - spacing
    x, y = xy
    if anchor_center:
        x -= w / 2
    for c in text:
        draw.text((x, y), c, font=fnt, fill=fill)
        x += draw.textlength(c, font=fnt) + spacing


class Composer:
    def __init__(self, spec, preset):
        self.spec, pr = spec, PRESETS[preset]
        self.W, self.H = pr["canvas"]
        self.k = self.W / BASE[0]
        self.region = (0, int(REGION_Y * self.k))
        self.bg = self._background()
        self.layers = [self._scene_layer(s) for s in spec.SCENES]
        self.static = self._static_layer()

    def S(self, v):
        return int(round(v * self.k))

    def _background(self):
        top, bot = (10, 16, 27), (18, 30, 46)
        g = Image.linear_gradient("L").resize((self.W, self.H))
        im = Image.composite(Image.new("RGB", (self.W, self.H), bot), Image.new("RGB", (self.W, self.H), top), g)
        glow = Image.new("RGB", (self.W, self.H), (30, 80, 110))
        mask = Image.new("L", (self.W, self.H), 0)
        ImageDraw.Draw(mask).ellipse((-self.W * .2, self.H * .22, self.W * 1.2, self.H * .78), fill=70)
        mask = mask.filter(ImageFilter.GaussianBlur(self.S(160)))
        return Image.composite(glow, im, mask).convert("RGBA")

    def _static_layer(self):
        im = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        f = font("Medium", self.S(25))
        d.text((self.W / 2, self.S(1808)), "IDEALIZED MOTION  ·  SCHEMATIC FORCE ARROWS", font=f, fill=(140, 160, 180, 150), anchor="mm")
        # leyenda de convenciones
        items = [("force", "Force"), ("torque", "Torque"), ("disp", "Displacement")]
        x = self.S(96)
        fl = font("Medium", self.S(26))
        for key, name in items:
            d.rounded_rectangle((x, self.S(1423), x + self.S(34), self.S(1431)), radius=4, fill=COL[key])
            d.text((x + self.S(46), self.S(1428)), name, font=fl, fill=(185, 200, 215, 210), anchor="lm")
            x += self.S(46) + d.textlength(name, font=fl) + self.S(40)
        return im

    def _scene_layer(self, s):
        im = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        spaced(d, (self.W / 2, self.S(132)), s["kicker"], font("SemiBold", self.S(28)), (72, 225, 214, 255), self.S(4), True)
        d.multiline_text((self.W / 2, self.S(196)), s["title"], font=font("Bold", self.S(66)), fill=(245, 248, 252, 255),
                         anchor="ma", align="center", spacing=self.S(10))
        d.line((self.S(300), self.S(352), self.S(780), self.S(352)), fill=(72, 225, 214, 160), width=max(2, self.S(3)))
        if s["eq"]:
            d.text((self.W / 2, self.S(1520)), s["eq"], font=font("SemiBold", self.S(92)), fill=(255, 255, 255, 255), anchor="mm")
            d.text((self.W / 2, self.S(1600)), s["sub"], font=font("Medium", self.S(31)), fill=(150, 205, 215, 255), anchor="mm")
        d.multiline_text((self.W / 2, self.S(1660)), self._wrap(s["caption"], d, font("Regular", self.S(38)), self.S(900)),
                         font=font("Regular", self.S(38)), fill=(215, 225, 235, 255), anchor="ma", align="center", spacing=self.S(8))
        return im

    @staticmethod
    def _wrap(text, d, fnt, maxw):
        out, line = [], ""
        for w in text.split():
            t = (line + " " + w).strip()
            if d.textlength(t, font=fnt) > maxw:
                out.append(line); line = w
            else:
                line = t
        out.append(line)
        return "\n".join(out)

    def frame(self, t, render_png, labels):
        sp = self.spec
        idx, ts = sp.scene_at(t)
        dur = sp.SCENES[idx]["dur"]
        im = self.bg.copy()
        r = Image.open(render_png).convert("RGBA")
        rw = self.W
        rh = int(round(r.height * rw / r.width))
        if r.size != (rw, rh):
            r = r.resize((rw, rh), Image.LANCZOS)
        # difuminado vertical de los bordes de la región 3D (sin cortes duros)
        f = self.S(130)
        ramp = Image.new("L", (1, rh), 255)
        ramp.putdata([int(255 * smooth(min(y, rh - 1 - y) / f)) for y in range(rh)])
        r.putalpha(ImageChops.multiply(r.getchannel("A"), ramp.resize((rw, rh))))
        im.alpha_composite(r, (self.region[0], self.region[1]))
        im.alpha_composite(self.static)

        a = smooth(ts / 0.5) * (1.0 if idx == len(sp.SCENES) - 1 else smooth((dur - ts) / 0.4))
        layer = self.layers[idx].copy()
        layer.putalpha(layer.getchannel("A").point(lambda v: int(v * a)))
        # leve deslizamiento hacia arriba al entrar
        im.alpha_composite(layer, (0, int(self.S(16) * (1 - smooth(ts / 0.5)))))

        d = ImageDraw.Draw(im, "RGBA")
        lf = font("SemiBold", self.S(40))
        sc = self.W / r.width
        for lb in labels:
            if "hud" in lb:
                hf = font("SemiBold", self.S(34))
                col = tuple(int(COL[lb["color"]].lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
                hy = self.region[1] + self.S(70) + lb["hud"] * self.S(66)
                w = d.textlength(lb["text"], font=hf)
                d.rounded_rectangle((self.S(40), hy - self.S(30), self.S(40) + w + self.S(36), hy + self.S(30)), radius=self.S(16), fill=(8, 14, 24, int(190 * lb["alpha"])))
                d.text((self.S(58), hy), lb["text"], font=hf, fill=col + (int(255 * lb["alpha"]),), anchor="lm")
                continue
            x = lb["x"] * sc + self.region[0]
            y = lb["y"] * (rh / PRESETS_H(r)) if False else lb["y"] * sc + self.region[1]
            y = min(max(y, self.region[1] + self.S(130)), self.region[1] + rh - self.S(90))
            al = int(255 * lb["alpha"])
            col = tuple(int(COL[lb["color"]].lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
            w = d.textlength(lb["text"], font=lf)
            px, py = self.S(16), self.S(8)
            anchor = lb.get("anchor", "l")
            x0 = x - w - px * 2 if anchor == "r" else x
            x0 = min(max(x0, self.S(20)), self.W - w - px * 2 - self.S(20))
            d.rounded_rectangle((x0, y - self.S(26) - py, x0 + w + px * 2, y + self.S(26) + py), radius=self.S(18), fill=(8, 14, 24, int(190 * lb["alpha"])))
            d.text((x0 + px, y), lb["text"], font=lf, fill=col + (al,), anchor="lm")

        # barra de progreso
        tot = sp.total_duration()
        d.rectangle((0, 0, self.W, self.S(8)), fill=(255, 255, 255, 25))
        d.rectangle((0, 0, self.W * min(1.0, t / tot), self.S(8)), fill=(72, 225, 214, 255))
        return im.convert("RGB")


def PRESETS_H(r):
    return r.height


def encode(frames_iter, out_path, fps, size):
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{size[0]}x{size[1]}",
           "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", out_path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for im in frames_iter:
        p.stdin.write(im.tobytes())
    p.stdin.close()
    p.wait()
