"""Kit reutilizable para Blender (bpy): materiales, primitivas, rosca, flechas físicas, escenario."""
import math
import bmesh
import bpy
from mathutils import Vector, Quaternion
from bpy_extras.object_utils import world_to_camera_view

from mech.blender.palette import COL  # noqa: E402


def _lin(c):
    c = c.lstrip("#")
    return tuple(((int(c[i:i + 2], 16) / 255) ** 2.2) for i in (0, 2, 4)) + (1.0,)


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    return bpy.context.scene


def material(name, color, metallic=0.0, rough=0.5, emit=0.0, alpha=1.0, coat=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = _lin(color)
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Roughness"].default_value = rough
    b.inputs["Alpha"].default_value = alpha
    if coat:
        b.inputs["Coat Weight"].default_value = coat
        b.inputs["Coat Roughness"].default_value = 0.08
    if emit:
        b.inputs["Emission Color"].default_value = _lin(color)
        b.inputs["Emission Strength"].default_value = emit
    return m


def knurl_material(name, color, pitch=0.0025):
    """Acero con estriado cruzado (rombos) mediante relieve procedural en coordenadas de objeto."""
    m = material(name, color, metallic=0.35, rough=0.42)
    nt = m.node_tree
    coord = nt.nodes.new("ShaderNodeTexCoord")
    waves = []
    for direction in ("Y", "Z"):
        w = nt.nodes.new("ShaderNodeTexWave")
        w.wave_type = "BANDS"
        w.bands_direction = direction
        w.wave_profile = "SAW"
        w.inputs["Scale"].default_value = 2 * math.pi / (pitch * 20)   # Wave multiplica la frecuencia por 20 internamente
        w.inputs["Distortion"].default_value = 0.0
        nt.links.new(coord.outputs["Object"], w.inputs["Vector"])
        waves.append(w)
    add = nt.nodes.new("ShaderNodeMath")
    add.operation = "ADD"
    nt.links.new(waves[0].outputs["Fac"], add.inputs[0])
    nt.links.new(waves[1].outputs["Fac"], add.inputs[1])
    half = nt.nodes.new("ShaderNodeMath")
    half.operation = "MULTIPLY"
    half.inputs[1].default_value = 0.5
    nt.links.new(add.outputs["Value"], half.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.035, 0.04, 0.05, 1)   # surcos
    ramp.color_ramp.elements[1].color = (0.42, 0.45, 0.50, 1)    # crestas
    nt.links.new(half.outputs["Value"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], nt.nodes["Principled BSDF"].inputs["Base Color"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 1.0
    bump.inputs["Distance"].default_value = 0.0012
    nt.links.new(add.outputs["Value"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], nt.nodes["Principled BSDF"].inputs["Normal"])
    return m


def set_alpha(mat, a):
    mat.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = a


def _finish(obj, mat, bevel=0.0015, smooth=True, harden=True):
    obj.data.materials.append(mat)
    if smooth:
        for p in obj.data.polygons:
            p.use_smooth = True
    if bevel:
        m = obj.modifiers.new("bevel", "BEVEL")
        m.width = bevel
        m.segments = 3
        m.limit_method = "ANGLE"
        m.harden_normals = harden
    return obj


def _obj(name, mesh_fn):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    mesh_fn(bm)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    return o


def box(name, x, y, z, mat, bevel=0.0015):
    """Caja alineada a ejes por rangos (min,max) en m; dimensiones reales (sin escalar)."""
    def fn(bm):
        bmesh.ops.create_cube(bm, size=1.0)
        for v in bm.verts:
            v.co.x = x[0] if v.co.x < 0 else x[1]
            v.co.y = y[0] if v.co.y < 0 else y[1]
            v.co.z = z[0] if v.co.z < 0 else z[1]
    thin = min(x[1] - x[0], y[1] - y[0], z[1] - z[0]) < 0.01   # harden_normals da normales nulas (negro) en placas finas
    return _finish(_obj(name, fn), mat, bevel, smooth=not thin, harden=not thin)


def cyl_x(name, x0, x1, radius, mat, center=(0, 0), seg=48, bevel=0.0008):
    """Cilindro con eje en X entre x0 y x1; center=(y,z)."""
    def fn(bm):
        bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=radius, radius2=radius, depth=x1 - x0)
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=__import__("mathutils").Matrix.Rotation(math.pi / 2, 3, "Y"))
        bmesh.ops.translate(bm, verts=bm.verts, vec=((x0 + x1) / 2, center[0], center[1]))
    return _finish(_obj(name, fn), mat, bevel)


def cyl_z(name, z0, z1, radius, mat, center=(0, 0), seg=64, bevel=0.0008):
    def fn(bm):
        bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=radius, radius2=radius, depth=z1 - z0)
        bmesh.ops.translate(bm, verts=bm.verts, vec=(center[0], center[1], (z0 + z1) / 2))
    return _finish(_obj(name, fn), mat, bevel)


def cyl_y_local(name, y0, y1, radius, mat, x=0.0, z=0.0, seg=24):
    """Cilindro con eje en Y (p. ej. barra de manivela) en coordenadas locales del padre."""
    def fn(bm):
        bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=radius, radius2=radius, depth=y1 - y0)
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=__import__("mathutils").Matrix.Rotation(math.pi / 2, 3, "X"))
        bmesh.ops.translate(bm, verts=bm.verts, vec=(x, (y0 + y1) / 2, z))
    return _finish(_obj(name, fn), mat, 0.0004)


def sphere(name, center, radius, mat):
    def fn(bm):
        bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=radius)
        bmesh.ops.translate(bm, verts=bm.verts, vec=center)
    return _finish(_obj(name, fn), mat, bevel=0)


def thread_x(name, length, lead, r_root, r_crest, mat, seg=36):
    """Rosca helicoidal a derecha a lo largo de +X (eje en origen). Perfil trapezoidal barrido."""
    steps = int(length / lead * seg)
    prof = [(-0.40 * lead, r_root), (-0.08 * lead, r_crest), (0.08 * lead, r_crest), (0.40 * lead, r_root)]

    def fn(bm):
        rings = []
        for i in range(steps + 1):
            s = i / seg
            a = 2 * math.pi * s
            ring = [bm.verts.new((lead * s + dx, r * math.cos(a), r * math.sin(a))) for dx, r in prof]
            rings.append(ring)
        for r0, r1 in zip(rings, rings[1:]):
            for k in range(4):
                bm.faces.new((r0[k], r0[(k + 1) % 4], r1[(k + 1) % 4], r1[k]))
        bm.faces.new(rings[0])
        bm.faces.new(rings[-1][::-1])
    o = _obj(name, fn)
    # núcleo
    core = cyl_x(name + "_core", 0, length, r_root * 0.96, mat, bevel=0, seg=32)
    core.parent = o
    return _finish(o, mat, bevel=0)


def empty(name, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None)
    e.location = loc
    bpy.context.collection.objects.link(e)
    return e


# ------------------------- Flechas físicas -------------------------
class Arrow:
    """Flecha 3D con punto de aplicación (origin) y vector; longitud proporcional a |vec| (esquemática)."""

    def __init__(self, name, color, radius=0.0022, head_r=0.0075, head_len=0.018, head=True, emit=0.45):
        self.mat = material(name, color, rough=0.35, emit=emit)
        self.head_len0 = head_len
        self.has_head = head

        def shaft(bm):
            bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=radius, radius2=radius, depth=1.0)
            bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, 0.5))
        self.shaft = _finish(_obj(name + "_s", shaft), self.mat, bevel=0)
        self.head = None
        if head:
            def hd(bm):
                bmesh.ops.create_cone(bm, cap_ends=True, segments=20, radius1=head_r, radius2=0.0, depth=1.0)
                bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, 0.5))
            self.head = _finish(_obj(name + "_h", hd), self.mat, bevel=0)
        for o in self.objs():
            o.visible_shadow = False
            o.rotation_mode = "QUATERNION"
        self.hide()

    def objs(self):
        return [self.shaft] + ([self.head] if self.head else [])

    def hide(self, h=True):
        for o in self.objs():
            o.hide_render = h
            o.hide_viewport = h

    def update(self, origin, vec, grow=1.0):
        v = Vector(vec)
        length = v.length * grow
        if length < 1e-4 or grow <= 0.01:
            self.hide()
            return
        self.hide(False)
        d = v.normalized()
        q = Vector((0, 0, 1)).rotation_difference(d)
        hl = min(self.head_len0, 0.4 * length) if self.has_head else 0.0
        o = Vector(origin)
        self.shaft.location = o
        self.shaft.rotation_quaternion = q
        self.shaft.scale = (1, 1, max(length - hl * 0.9, 1e-4))
        if self.head:
            self.head.location = o + d * (length - hl)
            self.head.rotation_quaternion = q
            self.head.scale = (1, 1, hl)


class ArcArrow:
    """Flecha curva (torque) alrededor del eje X en el punto center; ángulo medido en el plano YZ."""

    def __init__(self, name, color, radius=0.0022, head_r=0.0075):
        self.mat = material(name, color, rough=0.35, emit=0.45)
        self.r = radius
        self.head_r = head_r
        me = bpy.data.meshes.new(name)
        self.obj = bpy.data.objects.new(name, me)
        bpy.context.collection.objects.link(self.obj)
        self.obj.data.materials.append(self.mat)
        self.obj.visible_shadow = False
        self.obj.hide_render = self.obj.hide_viewport = True

    def update(self, center, R, a0, sweep, grow=1.0):
        """Arco desde a0 recorriendo 'sweep' rad (negativo = sentido horario visto desde +X)."""
        sweep *= grow
        me = self.obj.data
        if abs(sweep) < 0.05:
            self.obj.hide_render = self.obj.hide_viewport = True
            return
        self.obj.hide_render = self.obj.hide_viewport = False
        bm = bmesh.new()
        n = max(8, int(abs(sweep) / 0.12))
        sgn = 1 if sweep > 0 else -1
        head_ang = 0.30
        body = abs(sweep) - head_ang
        cx, cy, cz = center
        rings = []
        for i in range(n + 1):
            a = a0 + sgn * body * i / n
            ring = []
            for k in range(10):
                t = 2 * math.pi * k / 10
                rr = R + self.r * math.cos(t)
                dx = self.r * math.sin(t)
                ring.append(bm.verts.new((cx + dx, cy + rr * math.cos(a), cz + rr * math.sin(a))))
            rings.append(ring)
        for r0, r1 in zip(rings, rings[1:]):
            for k in range(10):
                bm.faces.new((r0[k], r0[(k + 1) % 10], r1[(k + 1) % 10], r1[k]))
        # cabeza cónica tangente
        a_b = a0 + sgn * body
        a_t = a0 + sgn * abs(sweep)
        base = []
        for k in range(10):
            t = 2 * math.pi * k / 10
            rr = R + self.head_r * math.cos(t)
            dx = self.head_r * math.sin(t)
            base.append(bm.verts.new((cx + dx, cy + rr * math.cos(a_b), cz + rr * math.sin(a_b))))
        tip = bm.verts.new((cx, cy + R * math.cos(a_t), cz + R * math.sin(a_t)))
        for k in range(10):
            bm.faces.new((base[k], base[(k + 1) % 10], tip))
        bm.to_mesh(me)
        bm.free()
        for p in me.polygons:
            p.use_smooth = True


# ------------------------- Escenario -------------------------
def setup_stage(scene, w, h, samples, fps, bounces=6):
    r = scene.render
    r.engine = "CYCLES"
    r.resolution_x, r.resolution_y, r.resolution_percentage = w, h, 100
    r.fps = fps
    r.film_transparent = True
    r.image_settings.file_format = "PNG"
    r.image_settings.color_mode = "RGBA"
    r.image_settings.compression = 3
    c = scene.cycles
    c.device = "CPU"
    c.samples = samples
    c.use_adaptive_sampling = True
    c.adaptive_threshold = 0.03
    c.use_denoising = True
    c.denoiser = "OPENIMAGEDENOISE"
    c.denoising_input_passes = "RGB_ALBEDO_NORMAL"
    c.denoising_prefilter = "FAST"
    bpy.context.view_layer.cycles.denoising_store_passes = True
    c.max_bounces = bounces
    c.diffuse_bounces = min(3, bounces)
    c.glossy_bounces = bounces
    c.transmission_bounces = 2
    c.transparent_max_bounces = 4
    c.use_animated_seed = False   # ruido fijo en pantalla: evita parpadeo entre fotogramas
    c.seed = 7
    c.sample_clamp_indirect = 8
    scene.view_settings.view_transform = "Filmic"
    scene.view_settings.look = "Medium High Contrast"
    scene.view_settings.exposure = -1.2
    scene.render.threads_mode = "AUTO"
    scene.render.use_persistent_data = True   # reutiliza BVH/escena entre fotogramas

    # Mundo de estudio (solo ilumina/refleja; el fondo es transparente)
    world = bpy.data.worlds.new("studio")
    world.use_nodes = True
    nt = world.node_tree
    bg = nt.nodes["Background"]
    bg.inputs["Strength"].default_value = 0.22
    grad = nt.nodes.new("ShaderNodeTexGradient")
    coord = nt.nodes.new("ShaderNodeTexCoord")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(coord.outputs["Generated"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], ramp.inputs[0])
    ramp.color_ramp.elements[0].color = (0.05, 0.08, 0.12, 1)
    ramp.color_ramp.elements[1].color = (0.40, 0.50, 0.65, 1)
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    scene.world = world

    # Suelo captador de sombras (contacto suave sobre fondo transparente)
    bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0, -0.35))
    floor = bpy.context.object
    floor.name = "floor"
    floor.is_shadow_catcher = True

    def softbox(name, loc, size, energy, color=(1, 1, 1)):
        d = bpy.data.lights.new(name, "AREA")
        d.shape = "RECTANGLE"
        d.size, d.size_y = size
        d.energy = energy
        d.color = color
        o = bpy.data.objects.new(name, d)
        bpy.context.collection.objects.link(o)
        o.location = loc
        direction = Vector((0.06, 0, 0.05)) - Vector(loc)
        o.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
        return o
    softbox("key", (-0.55, -0.55, 0.65), (0.6, 0.35), 28)
    softbox("fill", (0.7, -0.35, 0.35), (0.7, 0.4), 12, (0.85, 0.92, 1.0))
    softbox("rim", (0.25, 0.65, 0.5), (0.8, 0.2), 30, (0.9, 0.95, 1.0))
    softbox("top", (0.05, 0.0, 0.85), (0.5, 0.5), 6)
    softbox("macro", (0.10, 0.0, 0.26), (0.10, 0.12), 2.5)

    cam_d = bpy.data.cameras.new("cam")
    cam = bpy.data.objects.new("cam", cam_d)
    bpy.context.collection.objects.link(cam)
    scene.camera = cam
    cam_d.sensor_width = 36
    cam_d.clip_start = 0.01
    cam_d.clip_end = 20
    cam_d.dof.use_dof = True
    cam_d.dof.aperture_fstop = 14.0
    return cam


def aim_camera(cam, az_deg, el_deg, dist, target, focal):
    az, el = math.radians(az_deg), math.radians(el_deg)
    t = Vector(target)
    pos = t + Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el))) * dist
    cam.location = pos
    cam.rotation_euler = (t - pos).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = focal
    cam.data.dof.focus_distance = dist


def project(scene, cam, point):
    """Punto 3D -> píxeles (x, y desde arriba) dentro del área renderizada."""
    bpy.context.view_layer.update()   # la cámara cambió en este fotograma: refrescar matrices
    co = world_to_camera_view(scene, cam, Vector(point))
    return co.x * scene.render.resolution_x, (1 - co.y) * scene.render.resolution_y
