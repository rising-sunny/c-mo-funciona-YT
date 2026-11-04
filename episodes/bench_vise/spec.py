"""Especificación del episodio (solo datos, sin bpy). Unidades SI."""
from mech import physics as ph

# --- Parámetros físicos del modelo (ideal, sin fricción) ---
LEAD = 0.004          # avance por vuelta L [m]
R_HANDLE = 0.065      # brazo de la manivela r [m]
F_APPLIED = 20.0      # fuerza perpendicular aplicada [N]
WORK_W = 0.040        # ancho de la pieza [m]
GAP0 = 0.056          # apertura inicial entre mordazas [m]
TURNS_CONTACT = (GAP0 - WORK_W) / LEAD   # vueltas hasta tocar la pieza (=4)

TAU = ph.torque(R_HANDLE, F_APPLIED)             # 1.3 N·m
F_CLAMP = ph.ideal_axial_force(TAU, LEAD)         # ≈ 2.04 kN (ideal)

# Cada plano: cámara a→b (az°, el°, dist m, target, focal mm) con empuje/órbita continuos dentro del plano.
def C(az, el, dist, target, focal):
    return dict(az=az, el=el, dist=dist, target=target, focal=focal)


SCENES = [
    dict(id="hook", say="How can one tiny twist crush a solid block of metal? Let's open this vise up!", dur=4.5, kicker="01 / THE QUESTION",
         title="How can one hand\ncrush this tight?",
         caption="A bench vise turns a gentle twist into a huge squeeze.", eq=None, sub=None,
         cam=(C(20, 24, 0.52, (0.07, 0, 0.055), 45), C(58, 20, 0.42, (0.08, 0, 0.06), 50))),
    dict(id="face", say='First, the jaws. See that waffle pattern? Pure grip.', dur=4.0, kicker="02 / THE GRIP FACES",
         title="Textured jaws\nbite the workpiece",
         caption="A cross-hatched surface resists slipping.", eq=None, sub=None,
         cam=(C(60, 46, 0.34, (0.0, 0.0, 0.072), 60), C(82, 38, 0.26, (0.0, 0.0, 0.074), 75))),
    dict(id="torque", say='Now the handle. Push far from the center, and you make torque. Twenty newtons, times sixty-five millimeters... one point three newton-meters!', dur=7.5, kicker="03 / FORCE BECOMES TORQUE",
         title="A push at the\nhandle makes torque",
         caption="Push perpendicular to the handle, far from the axis.",
         eq="τ = r · F", sub=f"r = {R_HANDLE:.3f} m   ·   F = {F_APPLIED:.0f} N   →   τ = {TAU:.1f} N·m",
         cam=(C(62, 16, 0.58, (0.22, 0, 0.035), 55), C(84, 12, 0.44, (0.235, 0, 0.04), 65))),
    dict(id="thread", say='Inside, a thread turns every spin into forward motion. One full turn? Exactly four millimeters.', dur=6.0, kicker="04 / THREADS INTO MOTION",
         title="The thread turns\nspin into travel",
         caption="One full turn pushes the screw forward by exactly one lead.",
         eq="Δx = L · n", sub=f"L = {LEAD*1000:.0f} mm per turn   →   1 turn = {LEAD*1000:.0f} mm",
         cam=(C(12, 28, 0.36, (0.13, 0, 0.055), 60), C(-22, 22, 0.27, (0.125, 0, 0.056), 75))),
    dict(id="close", say='Four turns later, the jaw has crossed sixteen millimeters. And... contact!', dur=5.6, kicker="05 / CLOSING THE GAP",
         title="The jaw glides in\nuntil it touches",
         caption="Four turns close the 16 mm gap to the workpiece.",
         eq="Δx = n · L", sub=f"4 turns × {LEAD*1000:.0f} mm = {TURNS_CONTACT*LEAD*1000:.0f} mm",
         cam=(C(30, 22, 0.40, (0.05, 0, 0.07), 60), C(10, 26, 0.30, (0.035, 0, 0.08), 70))),
    dict(id="grip", say='Now the force. Torque times two pi, divided by the lead. About two thousand newtons, from one hand! Real life loses some to friction, but still!', dur=7.0, kicker="06 / SMALL TURNS, FIRM GRIP",
         title="Tiny motion,\nenormous force",
         caption="Ideal model: no friction. Real clamping loses part to friction.",
         eq="F = 2π · τ / L", sub=f"2π × {TAU:.1f} N·m / {LEAD*1000:.0f} mm  ≈  {F_CLAMP/1000:.1f} kN",
         cam=(C(38, 24, 0.40, (0.04, 0, 0.085), 65), C(18, 20, 0.30, (0.02, 0, 0.09), 80))),
    dict(id="outro", say='Twist in. Squeeze out. Follow for more machines, explained from the inside!', dur=5.0, kicker="07 / THE WHOLE STORY",
         title="Twist in.\nSqueeze out.",
         caption="Torque turns into travel, and travel into clamping force.",
         eq="τ → Δx → F", sub="idealized — real vises lose part of this to friction",
         cam=(C(18, 22, 0.34, (0.05, 0, 0.07), 55), C(150, 28, 0.62, (0.07, 0, 0.05), 40))),
]

CAM_BLEND = 1.3  # s de transición suave desde la pose final del plano anterior


def sid(name):
    return [s["id"] for s in SCENES].index(name)


def start(name):
    return scene_start(sid(name))


def end(name):
    return start(name) + SCENES[sid(name)]["dur"]


def _at(name, frac):
    return start(name) + frac * SCENES[sid(name)]["dur"]


def _turn_keys():
    """Vueltas n(t) ancladas a fracciones de cada plano (robusto a cambios de duración)."""
    return [(0.0, 0.0), (_at("hook", 0.35), 0.0), (end("hook"), 0.2),
            (end("face"), 0.2),
            (_at("torque", 0.25), 0.2), (_at("torque", 0.9), 1.2),
            (_at("thread", 0.15), 1.2), (_at("thread", 0.9), 2.2),
            (_at("close", 0.12), 2.2), (_at("close", 0.82), TURNS_CONTACT)]


def total_duration():
    return sum(s["dur"] for s in SCENES)


def scene_at(t):
    acc = 0.0
    for i, s in enumerate(SCENES):
        if t < acc + s["dur"] or i == len(SCENES) - 1:
            return i, t - acc
        acc += s["dur"]


def scene_start(i):
    return sum(s["dur"] for s in SCENES[:i])


def turns_at(t):
    """Vueltas acumuladas del tornillo, limitadas por el contacto con la pieza."""
    keys = _turn_keys() + [(1e9, TURNS_CONTACT)]
    if t <= keys[0][0]:
        n = keys[0][1]
    elif t >= keys[-1][0]:
        n = keys[-1][1]
    else:
        n = keys[-1][1]
        for (t0, n0), (t1, n1) in zip(keys, keys[1:]):
            if t0 <= t <= t1:
                n = ph.lerp(n0, n1, ph.smoothstep((t - t0) / (t1 - t0)))
                break
    return min(n, TURNS_CONTACT)


def cam_pose(t):
    """Pose de cámara en t: empuje/órbita dentro del plano + mezcla desde el final del plano anterior."""
    i, ts = scene_at(t)
    a, b = SCENES[i]["cam"]
    mix = lambda x, y, w: {k: (ph.lerp(x[k], y[k], w) if k != "target" else tuple(ph.lerp(x[k][j], y[k][j], w) for j in range(3))) for k in x}
    pose = mix(a, b, ph.smoothstep(ts / SCENES[i]["dur"]))
    if i > 0:
        pose = mix(SCENES[i - 1]["cam"][1], pose, ph.smoothstep(ts / CAM_BLEND))
    return pose


def clamp_grow(t):
    """0→1 tras el contacto: crecimiento esquemático de las fuerzas de apriete."""
    t_start = start("grip") + 0.3
    return ph.smoothstep((t - t_start) / 1.6)


def lead_adv(n):
    return ph.lead_advance(LEAD, n)


def _apply_timing():
    import json, os
    path = os.path.join(os.path.dirname(__file__), "timing.json")
    if os.path.exists(path):
        t = json.load(open(path))
        for sc in SCENES:
            if sc["id"] in t:
                sc["dur"] = t[sc["id"]]["dur"]
                sc["lines"] = t[sc["id"]]["lines"]
                sc["lead"] = t[sc["id"]]["lead"]


_apply_timing()
