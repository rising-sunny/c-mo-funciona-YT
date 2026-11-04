"""Texto animado (pop con rebote, entrada por palabras/caracteres) y subtítulos virales palabra a palabra."""
import os, re
from PIL import Image, ImageDraw, ImageFont

FONT_DIR = "/usr/share/fonts/opentype/inter/"
YELLOW, WHITE, CYAN = (255, 225, 77), (255, 255, 255), (72, 225, 214)


def font(weight, size):
    p = FONT_DIR + f"Inter-{weight}.otf"
    if not os.path.exists(p):
        p = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    return ImageFont.truetype(p, size)


def ease_out_back(u, s=1.9):
    u = min(1.0, max(0.0, u)) - 1
    return 1 + (s + 1) * u ** 3 + s * u ** 2


def ease_out_cubic(u):
    u = min(1.0, max(0.0, u))
    return 1 - (1 - u) ** 3


def text_sprite(text, fnt, fill, stroke=0, stroke_fill=(0, 0, 0), pad=None):
    """RGBA con color uniforme y alfa de la tipografía (evita halos al reescalar)."""
    pad = pad if pad is not None else stroke + 6
    probe = ImageDraw.Draw(Image.new("L", (1, 1)))
    l, t, r, b = probe.textbbox((0, 0), text, font=fnt, stroke_width=stroke)
    w, h = int(r - l + 2 * pad), int(b - t + 2 * pad)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).text((pad - l, pad - t), text, font=fnt, fill=255)
    out = Image.new("RGBA", (w, h), fill + (0,))
    out.putalpha(mask)
    if stroke:
        sm = Image.new("L", (w, h), 0)
        ImageDraw.Draw(sm).text((pad - l, pad - t), text, font=fnt, fill=255, stroke_width=stroke, stroke_fill=255)
        base = Image.new("RGBA", (w, h), stroke_fill + (0,))
        base.putalpha(sm)
        base.alpha_composite(out)
        out = base
    return out


def blit(im, sprite, cx, cy, scale=1.0, alpha=1.0):
    if alpha <= 0.01 or scale <= 0.01:
        return
    if abs(scale - 1.0) > 0.005:
        sprite = sprite.resize((max(1, int(sprite.width * scale)), max(1, int(sprite.height * scale))), Image.BILINEAR)
    if alpha < 0.99:
        a = sprite.getchannel("A").point(lambda v: int(v * alpha))
        sprite = sprite.copy()
        sprite.putalpha(a)
    im.paste(sprite, (int(cx - sprite.width / 2), int(cy - sprite.height / 2)), sprite)


class Motion:
    def __init__(self, spec, k, W):
        self.spec, self.k, self.W = spec, k, W
        S = lambda v: int(round(v * k))
        self.S = S
        self.scenes = [self._build_scene(s) for s in spec.SCENES]
        self.groups = self._build_subs()
        self.sub_font = font("Black", S(98))
        self._cache = {}

    # ---------------- textos de plano ----------------
    def _build_scene(self, s):
        S, W = self.S, self.W
        items = []  # (sprite, cx, cy, t_in, kind)
        kf = font("SemiBold", S(28))
        kick = text_sprite(self._spaced(s["kicker"]), kf, CYAN)
        items.append((kick, W / 2, S(142), 0.00, "slide"))
        tf = font("Black", S(70))
        probe = ImageDraw.Draw(Image.new("L", (1, 1)))
        y = S(228)
        wi = 0
        for line in s["title"].split("\n"):
            words = line.split()
            wl = [probe.textlength(w, font=tf) for w in words]
            sp = probe.textlength(" ", font=tf)
            x = W / 2 - (sum(wl) + sp * (len(words) - 1)) / 2
            for w, ww in zip(words, wl):
                items.append((text_sprite(w, tf, (246, 249, 252)), x + ww / 2, y, 0.12 + 0.085 * wi, "pop"))
                x += ww + sp
                wi += 1
            y += S(80)
        if s["eq"]:
            ef = font("Bold", S(96))
            t0 = 0.30 + 0.085 * wi + 0.25
            x = W / 2 - probe.textlength(s["eq"], font=ef) / 2
            for i, ch in enumerate(s["eq"]):
                pre = probe.textlength(s["eq"][:i], font=ef)
                cw = probe.textlength(ch, font=ef)
                if ch.strip():
                    items.append((text_sprite(ch, ef, (255, 255, 255)), x + pre + cw / 2, S(1530), t0 + 0.045 * i, "pop"))
            sf = font("Medium", S(31))
            items.append((text_sprite(s["sub"], sf, (150, 205, 215)), W / 2, S(1612), t0 + 0.045 * len(s["eq"]) + 0.15, "slide"))
        return items

    @staticmethod
    def _spaced(t):
        return " ".join(t) .replace("   ", "  ") if False else t

    def draw_scene(self, im, t):
        i, ts = self.spec.scene_at(t)
        dur = self.spec.SCENES[i]["dur"]
        out_v = max(0.0, (ts - (dur - 0.30)) / 0.30)
        if i == len(self.spec.SCENES) - 1:
            out_v = max(0.0, (ts - (dur - 0.15)) / 0.15)
        for sprite, cx, cy, t_in, kind in self.scenes[i]:
            u = (ts - t_in) / (0.42 if kind == "pop" else 0.38)
            if u <= 0:
                continue
            if kind == "pop":
                e = ease_out_back(u)
                scale, dy, a = 0.55 + 0.45 * e, 18 * (1 - ease_out_cubic(u)), min(1.0, u * 3)
            else:
                e = ease_out_cubic(u)
                scale, dy, a = 1.0, 26 * (1 - e), min(1.0, u * 2.5)
            blit(im, sprite, cx, cy + dy - self.S(26) * out_v, scale, a * (1 - out_v))

    # ---------------- subtítulos virales ----------------
    def _build_subs(self):
        groups = []
        for i, s in enumerate(self.spec.SCENES):
            t0 = self.spec.scene_start(i)
            for ln in s.get("lines", []):
                cur = []
                for w in ln["words"]:
                    txt = re.sub(r"[^\w'\-?!]", "", w["w"]).upper()
                    if not txt:
                        continue
                    cur.append(dict(txt=txt, start=t0 + w["start"], end=t0 + w["end"]))
                    if len(cur) >= 3 or sum(len(c["txt"]) for c in cur) > 15 or re.search(r"[.,?!…:]$", w["w"]):
                        groups.append(cur)
                        cur = []
                if cur:
                    groups.append(cur)
        return groups

    def _word(self, txt, color, scale_key):
        key = (txt, color)
        if key not in self._cache:
            self._cache[key] = text_sprite(txt, self.sub_font, color, stroke=self.S(11), stroke_fill=(10, 12, 20))
        return self._cache[key]

    def draw_subs(self, im, t):
        g = None
        for idx, grp in enumerate(self.groups):
            nxt = self.groups[idx + 1][0]["start"] if idx + 1 < len(self.groups) else 1e9
            if grp[0]["start"] - 0.03 <= t < min(grp[-1]["end"] + 0.12, nxt):
                g = grp
                break
        if not g:
            return
        S = self.S
        sprites = [(self._word(w["txt"], WHITE, 0), self._word(w["txt"], YELLOW, 0)) for w in g]
        gap = S(26)
        total = sum(s[0].width for s in sprites) + gap * (len(sprites) - 1)
        fit = min(1.0, (self.W - S(90)) / total)
        x = self.W / 2 - total * fit / 2
        cy = S(1338)
        t_first = g[0]["start"]
        group_pop = ease_out_back((t - (t_first - 0.03)) / 0.14, 1.4)
        for w, (white, yellow) in zip(g, sprites):
            active = w["start"] <= t < w["end"] + 0.02 or (t >= w["end"] and w is g[-1])
            sp = white if not active else yellow
            u = (t - w["start"]) / 0.16
            pop = 1.0 + (0.20 * (1 - ease_out_cubic(u)) + 0.07 if active else 0.0)
            cx = x + sp.width * fit / 2
            blit(im, sp, cx, cy, fit * pop * (0.85 + 0.15 * min(1.0, group_pop)), min(1.0, group_pop * 1.6))
            x += (sp.width + gap) * fit

    def draw(self, im, t):
        self.draw_scene(im, t)
        self.draw_subs(im, t)
