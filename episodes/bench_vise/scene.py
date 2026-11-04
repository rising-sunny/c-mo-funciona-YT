"""Modelo 3D del tornillo de banco + estado por fotograma. Se ejecuta dentro de Blender."""
import math
from mech import physics as ph
from mech.blender import kit
from mech.blender.kit import COL, Vector
from . import spec as S

AXIS_Z = 0.055
LS = 0.14  # longitud del tornillo
HOUSING = dict(x=(0.12, 0.15), y=(-0.03, 0.03), z=(0.040, 0.070))


def smoothwin(t, a, b, fade=0.7):
    """Ventana suave: 0→1 en [a, a+fade], 1→0 en [b-fade, b]."""
    return ph.smoothstep((t - a) / fade) * ph.smoothstep((b - t) / fade)


class Vise:
    def build(self, scene, cam):
        self.scene, self.cam = scene, cam
        body = kit.material("body", COL["body"], metallic=0.1, rough=0.42, coat=0.25)
        self.m_housing = kit.material("housing", COL["body"], metallic=0.1, rough=0.42, coat=0.25)
        dark = kit.material("dark", COL["dark"], rough=0.45)
        steel = kit.material("steel", COL["steel"], metallic=1.0, rough=0.28)
        brass = kit.material("brass", "#c9a24a", metallic=1.0, rough=0.3)
        knurl = kit.knurl_material("knurl", "#6f7882")
        work = kit.material("work", COL["work"], metallic=0.6, rough=0.4, coat=0.3)

        # Banco de trabajo (la manivela sobresale por delante y barre libre)
        wood = kit.material("bench", "#241c1a", rough=0.6)
        kit.box("bench", (-0.32, 0.185), (-0.22, 0.22), (-0.06, 0.0), wood, bevel=0.003)

        # Estructura fija
        kit.box("base", (-0.09, 0.17), (-0.09, 0.09), (0, 0.012), body, bevel=0.003)
        kit.cyl_z("swivel", 0.012, 0.022, 0.07, dark, center=(0.04, 0))
        kit.box("bed", (-0.07, 0.15), (-0.045, 0.045), (0.022, 0.040), body, bevel=0.003)
        kit.box("fixed_jaw", (-0.07, -0.0012), (-0.055, 0.055), (0.040, 0.100), body, bevel=0.003)
        kit.box("fixed_face", (-0.004, 0.0), (-0.05, 0.05), (0.050, 0.095), knurl, bevel=0.0004)
        for sy in (-0.040, 0.040):
            kit.cyl_x(f"fscrew{sy}", 0.0, 0.0016, 0.0035, steel, center=(sy, 0.0725), seg=16, bevel=0.0003)
        for i, (bx, by) in enumerate([(-0.07, -0.07), (-0.07, 0.07), (0.15, -0.07), (0.15, 0.07)]):
            kit.cyl_z(f"bolt{i}", 0.012, 0.0165, 0.006, steel, center=(bx, by), seg=6)
        kit.box("housing", HOUSING["x"], HOUSING["y"], HOUSING["z"], self.m_housing, bevel=0.002)
        self.housing = bpy_obj("housing")
        kit.cyl_x("nut", 0.123, 0.147, 0.0145, brass, center=(0, AXIS_Z), bevel=0.0006)

        # Mordaza móvil
        self.jaw = kit.empty("jaw_root")
        j = kit.box("moving_jaw", (0.0012, 0.05), (-0.055, 0.055), (0.040, 0.100), body, bevel=0.003)
        f = kit.box("moving_face", (0.0, 0.004), (-0.05, 0.05), (0.050, 0.095), knurl, bevel=0.0004)
        j.parent = f.parent = self.jaw
        for sy in (-0.040, 0.040):
            sc = kit.cyl_x(f"mscrew{sy}", -0.0016, 0.0, 0.0035, steel, center=(sy, 0.0725), seg=16, bevel=0.0003)
            sc.parent = self.jaw

        # Tornillo: traslación (screw_move) + giro (screw_spin) + manivela
        self.screw_move = kit.empty("screw_move", (0.106, 0, AXIS_Z))
        self.spin = kit.empty("screw_spin")
        self.spin.parent = self.screw_move
        collar = kit.cyl_x("collar", -0.004, 0.0, 0.0115, steel, bevel=0.0006)
        collar.parent = self.screw_move
        th = kit.thread_x("thread", 0.125, S.LEAD, 0.0072, 0.0092, steel)
        th.parent = self.spin
        hub = kit.cyl_x("hub", 0.125, 0.155, 0.0135, dark, bevel=0.001)
        hub.parent = self.spin
        ring = kit.cyl_x("retain", 0.155, 0.1585, 0.0105, steel, bevel=0.0004)
        ring.parent = self.spin
        mark = kit.box("mark", (0.127, 0.153), (-0.0022, 0.0022), (0.0124, 0.0141), kit_mat_mark(), bevel=0.0002)
        mark.parent = self.spin
        washer = kit.cyl_x("washer", 0.0, 0.0045, 0.0128, steel, bevel=0.0005)
        washer.parent = self.screw_move
        bar = kit.cyl_y_local("bar", -S.R_HANDLE, S.R_HANDLE, 0.0045, steel, x=0.14)
        bar.parent = self.spin
        for sgn in (-1, 1):
            b = kit.sphere(f"ball{sgn}", (0.14, sgn * S.R_HANDLE, 0), 0.0085, dark)
            b.parent = self.spin

        # Pieza de trabajo
        self.work = kit.box("workpiece", (0, S.WORK_W), (-0.03, 0.03), (0.040, 0.125), work, bevel=0.0015)

        # Anotaciones
        self.a_force = kit.Arrow("force", COL["force"])
        self.a_rline = kit.Arrow("rline", COL["white"], radius=0.0009, head=False, emit=0.35)
        self.a_torque = kit.ArcArrow("torque", COL["torque"])
        self.a_disp = kit.Arrow("disp", COL["disp"], radius=0.003, head_r=0.009, head_len=0.014)
        self.a_ref = kit.Arrow("ref", COL["disp"], radius=0.0009, head=False, emit=0.35)
        self.a_clampL = kit.Arrow("clampL", COL["force"], radius=0.002, head_r=0.0075, head_len=0.018)
        self.a_clampR = kit.Arrow("clampR", COL["force"], radius=0.002, head_r=0.0075, head_len=0.018)

    # ------------------------------------------------------------
    def apply(self, t):
        """Coloca el modelo/cámara en el instante t y devuelve las etiquetas 2D anclas."""
        n = S.turns_at(t)
        phi = -2 * math.pi * n                         # giro horario visto desde +X
        g = S.GAP0 - S.lead_adv(n)                     # apertura entre mordazas
        self.jaw.location = (g, 0, 0)
        self.screw_move.location = (g + 0.05, 0, AXIS_Z)
        self.spin.rotation_euler = (phi, 0, 0)

        pose = S.cam_pose(t)
        kit.aim_camera(self.cam, pose["az"], pose["el"], pose["dist"], pose["target"], pose["focal"])

        # La pieza sale de cuadro durante el plano macro y vuelve a caer entre las mordazas
        wz = 0.22 * ph.smoothstep((t - (S.end("hook") - 0.5)) / 1.0) * (1 - ph.smoothstep((t - (S.end("face") - 1.0)) / 1.3))
        self.work.location = (0, 0, wz)

        labels = []
        axis_pt = Vector((g + 0.05 + 0.14, 0, AXIS_Z))         # centro de la manivela
        hand_end = axis_pt + Vector((0, S.R_HANDLE * math.cos(phi), S.R_HANDLE * math.sin(phi)))
        tang = Vector((0, math.sin(phi), -math.cos(phi)))       # sentido horario (perpendicular a r)

        # --- Escena 2: fuerza, brazo y torque ---
        a = smoothwin(t, S.start("torque") + 0.4, S.end("torque") - 0.2)
        self.a_force.update(hand_end - tang * 0.0 , tang * 0.075, a)
        # el vector de fuerza parte del extremo y apunta en el sentido del giro
        self.a_rline.update(axis_pt, hand_end - axis_pt, a)
        self.a_torque.update(axis_pt + Vector((0.025, 0, 0)), 0.038, phi + math.radians(30), -math.radians(240), a)
        if a > 0.05:
            tip = hand_end + tang * 0.085
            labels.append(dict(text=f"F = {S.F_APPLIED:.0f} N", p=tuple(tip), color="force", alpha=a, dx=18, dy=-6))
            mid = axis_pt + (hand_end - axis_pt) * 0.5
            labels.append(dict(text=f"r = {S.R_HANDLE:.3f} m", p=tuple(mid), color="white", alpha=a, dx=-12, dy=26, anchor="r"))
            labels.append(dict(text="τ", p=tuple(axis_pt + Vector((0.025, 0.052 * math.cos(phi - math.pi / 2), 0.052 * math.sin(phi - math.pi / 2)))), color="torque", alpha=a, dx=-30, dy=-50))

        # --- Escenas 3 y 4: desplazamiento Δx medido desde el inicio de la escena ---
        for si in ("thread", "close"):
            w = smoothwin(t, S.start(si) + 0.6, S.end(si) - 0.2)
            if w <= 0.02:
                continue
            n0 = S.turns_at(S.start(si) + 0.6) if si == "thread" else 0.0
            dx = S.lead_adv(n - n0)
            if dx > 0.0015:
                x_ref = (S.GAP0 - S.lead_adv(n0)) + 0.05
                p0 = Vector((x_ref, 0.0, AXIS_Z + 0.024))
                self.a_ref.update(p0 + Vector((0, 0, -0.012)), Vector((0, 0, 0.024)), w)
                self.a_disp.update(p0 + Vector((0, 0, 0)), Vector((-dx, 0, 0)), w)
                labels.append(dict(text=f"Δx = {dx*1000:.1f} mm", p=tuple(p0 + Vector((-dx / 2, 0, -0.006))),
                                   color="disp", alpha=w, dx=0, dy=34))

        # --- Escena 5: fuerzas de apriete sobre la pieza (esquemáticas) ---
        grow = S.clamp_grow(t) * (1 - ph.smoothstep((t - S.start("outro")) / 0.8))
        L = 0.05
        z = 0.113
        self.a_clampL.update((-0.002 - L, -0.0, z), Vector((L, 0, 0)), grow)
        self.a_clampR.update((S.WORK_W + 0.002 + L, 0.0, z), Vector((-L, 0, 0)), grow)
        if grow > 0.05:
            labels.append(dict(text="F", p=(-0.04, 0, z), color="force", alpha=grow, dx=0, dy=-30))
            labels.append(dict(text="F", p=(S.WORK_W + 0.04, 0, z), color="force", alpha=grow, dx=0, dy=-30))

        # --- Corte: carcasa semitransparente en la escena del tornillo ---
        cut = smoothwin(t, S.start("thread") + 0.2, S.end("thread") + 0.4, fade=1.0)
        alpha = 1.0 - 0.82 * cut
        kit.set_alpha(self.m_housing, alpha)
        self.housing.visible_shadow = alpha > 0.9

        # HUD en vivo
        h = smoothwin(t, S.start("torque") + 0.3, S.end("grip") + 0.5)
        if h > 0.02:
            labels.append(dict(text=f"n = {n:4.2f} turns", hud=0, color="white", alpha=h))
            labels.append(dict(text=f"gap = {g*1000:4.1f} mm", hud=1, color="disp", alpha=h))

        # proyecciones a píxeles
        out = []
        for lb in labels:
            if "hud" in lb:
                out.append(lb)
                continue
            x, y = kit.project(self.scene, self.cam, lb["p"])
            lb = dict(lb)
            lb["x"], lb["y"] = x + lb.pop("dx", 0), y + lb.pop("dy", 0)
            lb.pop("p")
            out.append(lb)
        return out


def kit_mat_mark():
    return kit.material("mark", COL["torque"], rough=0.5, emit=0.6)


def bpy_obj(name):
    import bpy
    return bpy.data.objects[name]
