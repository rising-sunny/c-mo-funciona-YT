"""Procedural bench vise and storyboard. Blender 4.3+, all dimensions in metres."""
import argparse
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Vector
sys.path.insert(0, str(Path(__file__).parent))
from physics import motion, episode_progress
from camera_motion import camera_pose

parser = argparse.ArgumentParser()
parser.add_argument('--config', required=True)
parser.add_argument('--output', required=True)
parser.add_argument('--preview', action='store_true')
parser.add_argument('--stills', action='store_true')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
cfg = json.loads(Path(args.config).read_text())
p = cfg['physics']
out = Path(args.output)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
s = bpy.context.scene
s.render.engine = 'BLENDER_WORKBENCH'
s.display.shading.light = 'STUDIO'
s.display.render_aa = cfg.get('render_aa','8')
s.display.shading.studiolight_rotate_z = .5
s.display.shading.color_type = 'MATERIAL'
s.display.shading.show_shadows = True
s.display.shading.show_cavity = True
s.display.shading.cavity_type = 'BOTH'
s.display.shading.curvature_ridge_factor = 1.4
s.display.shading.curvature_valley_factor = 1.1
s.display.shading.show_specular_highlight = True
s.display.shading.background_type = 'WORLD'
s.world.color = (.018, .027, .043)
s.render.resolution_x = cfg['preview']['width'] if args.preview else cfg['width']
s.render.resolution_y = cfg['preview']['height'] if args.preview else cfg['height']
s.render.resolution_percentage = 100
s.render.fps = cfg['preview']['fps'] if args.preview else cfg['fps']
s.frame_end = round(cfg['duration'] * s.render.fps)
s.render.image_settings.file_format = 'PNG'
frames_path = out/'frames'
frames_path.mkdir(parents=True, exist_ok=True)
s.render.filepath = str(frames_path)+'/'
s.view_settings.view_transform = 'Standard'


def mat(name, color, metal=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.metallic = metal
    m.roughness = .3 if metal else .55
    return m

iron = mat('Enamel - deep workshop blue', (.045, .24, .39))
steel = mat('Brushed steel', (.56, .65, .71), .85)
dark = mat('Dark steel', (.12, .17, .21), .7)
brass = mat('Bronze fixed nut', (.8, .43, .12), .65)
gold = mat('Workpiece - warm orange', (.96, .45, .09))
cyan = mat('Hand force - cyan', (.05, .95, .86))
white = mat('Machined marks', (.87, .93, .96))

housing = []
moving = []
rotating = []
force_objects = []
cutaway_objects = []


def finish(o, name, material, group=None):
    o.name = name
    o.data.materials.append(material)
    if group is not None:
        group.append(o)
    return o


def box(name, xyz, dims, material, group=None, bevel=.002):
    bpy.ops.mesh.primitive_cube_add(size=1, location=xyz)
    o = bpy.context.object
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = o.modifiers.new('Soft machined edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        o.modifiers.new('Face normals', 'WEIGHTED_NORMAL')
    return finish(o, name, material, group)


def rod(name, a, b, radius, material, group=None, cone=False, vertices=32):
    d = Vector(b)-Vector(a)
    if cone:
        bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=radius, radius2=0, depth=d.length)
    else:
        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=d.length)
    o = bpy.context.object
    o.location = (Vector(a)+Vector(b))/2
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    for face in o.data.polygons:
        face.use_smooth = len(face.vertices) == 4
    return finish(o, name, material, group)


def sphere(name, xyz, radius, material, group):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=radius, location=xyz)
    o = bpy.context.object
    for poly in o.data.polygons:
        poly.use_smooth = True
    return finish(o, name, material, group)


def tube(name, points, radius, material, group=None):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = radius
    curve.bevel_resolution = 2
    poly = curve.splines.new('POLY')
    poly.points.add(len(points)-1)
    for point, co in zip(poly.points, points):
        point.co = (*co, 1)
    o = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(o)
    return finish(o, name, material, group)


# Broad bolted base, swivel ring and cast body make the silhouette recognizable.
box('Bench mounting foot', (-.055, 0, .012), (.205, .156, .024), iron)
rod('Swivel steel ring', (-.055, 0, .025), (-.055, 0, .034), .069, steel)
rod('Swivel blue casting', (-.055, 0, .034), (-.055, 0, .046), .064, iron)
for x in (-.13, .02):
    for y in (-.057, .057):
        rod('Hex mounting bolt', (x, y, .024), (x, y, .031), .007, dark, vertices=6)
        rod('Bolt washer', (x, y, .024), (x, y, .026), .010, steel)
box('Cast fixed body', (-.055, 0, .074), (.13, .095, .062), iron, housing, bevel=.009)
box('Rear fixed jaw support', (-.100, 0, .122), (.040, .095, .086), iron, housing, bevel=.005)
box('Rear anvil', (-.133, 0, .098), (.042, .085, .015), steel, housing)
# Fixed jaw grip plane is x=-.077. Piece ends at x=-.037.
fixed_plane = -.077
piece_right = -.037
box('Fixed jaw head', (-.096, 0, .158), (.035, .132, .035), iron)
box('Fixed replaceable steel jaw', (-.0785, 0, .158), (.003, .128, .030), steel)
box('Copper coloured workpiece', (-.057, 0, .166), (.040, .052, .047), gold)
travel = p['lead_m']*p['turns']
# Moving face left edge = centre-.0185-.0015.
end_jaw = piece_right+.020
start_jaw = end_jaw+travel
box('Moving jaw head', (start_jaw, 0, .158), (.035, .132, .035), iron, moving)
box('Moving replaceable steel jaw', (start_jaw-.0185, 0, .158), (.003, .128, .030), steel, moving)
box('Moving cast front support', (start_jaw+.004, 0, .122), (.043, .092, .055), iron, moving, bevel=.004)
box('Sliding rectangular guide', (start_jaw-.021, 0, .089), (.156, .054, .041), dark, moving)
# Surface details on the replaceable jaws: grip grooves and screw heads.
for side, center, group in [('Fixed', -.0785, None), ('Moving', start_jaw-.0185, moving)]:
    face_x = center + (.0016 if side == 'Fixed' else -.0016)
    for y in (-.047, .047):
        rod(side+' jaw plate fixing screw', (face_x-.0004, y, .158),
            (face_x+.0004, y, .158), .0033, dark, group, vertices=8)
    for y in [i*.006 for i in range(-6, 7)]:
        box(side+' grip groove', (face_x, y, .158), (.00035, .0008, .024), dark, group, bevel=0)
# Fine crosshatching on the steel grip faces, modelled in geometry for macro shots.
for side, center, group in [('Fixed', -.0785, None), ('Moving', start_jaw-.0185, moving)]:
    fx = center+(.00172 if side=='Fixed' else -.00172)
    for slope in (-1,1):
        for offset in [i*.003 for i in range(-8,9)]:
            # Clip diagonal grooves to the central portion of each grip plate.
            candidates=[]
            for y in (-.038,.038):
                z=slope*y+offset
                if -.013<=z<=.013: candidates.append((y,z))
            for z in (-.013,.013):
                y=(z-offset)/slope
                if -.038<=y<=.038: candidates.append((y,z))
            if len(candidates)>=2:
                a,b=candidates[:2]
                tube(side+' diagonal grip etching',[(fx,a[0],.158+a[1]),(fx,b[0],.158+b[1])],
                     .00013,dark,group)
    for y in (-.047,.047):
        tube(side+' screw head slot', [(fx+.0006,y-.002,.158),(fx+.0006,y+.002,.158)],
             .00025,steel,group)
# Cast ribs, bearing ring and an inset nameplate add readable manufactured details.
for x in (-.094,-.021):
    box('Casting strengthening rib', (x,-.048,.071),(.010,.004,.039),iron,bevel=.002)
box('Inset casting nameplate',(-.056,-.0485,.072),(.048,.002,.022),dark,bevel=.001)
text_curve=bpy.data.curves.new('Raised cast label','FONT')
text_curve.body='BV-04'
text_curve.size=.008
text_curve.align_x='CENTER'
text_curve.align_y='CENTER'
text_curve.extrude=.00013
label=bpy.data.objects.new('Raised cast label',text_curve)
bpy.context.collection.objects.link(label)
label.location=(-.056,-.0498,.072)
label.rotation_euler=(math.pi/2,0,0)
label.data.materials.append(steel)
for x in (-.076,-.036):
    rod('Nameplate rivet',(x,-.051,.072),(x,-.0495,.072),.0013,steel)
# A thin machined witness mark makes shaft rotation legible in close-up.
# Fixed nut is hidden by the casting until the explicitly labeled cutaway.
axis_z = .089
nut_x = -.061
# A real annular hex nut, not a solid block intersecting the screw.
verts, faces = [], []
for x, radius in [(nut_x-.014, .019), (nut_x+.014, .019),
                  (nut_x-.014, .0082), (nut_x+.014, .0082)]:
    for i in range(48):
        theta = 2*math.pi*i/48
        verts.append((x, radius*math.cos(theta), axis_z+radius*math.sin(theta)))
for i in range(48):
    j=(i+1)%48
    faces.extend([(i,j,48+j,48+i), (96+i,144+i,144+j,96+j),
                  (i,96+i,96+j,j), (48+i,48+j,144+j,144+i)])
mesh=bpy.data.meshes.new('Bored fixed nut mesh')
mesh.from_pydata(verts, [], faces)
nut=bpy.data.objects.new('Stationary bronze threaded nut', mesh)
bpy.context.collection.objects.link(nut)
finish(nut, nut.name, brass, cutaway_objects)
box('Cutaway fixed nut mount', (nut_x, 0, .050), (.037, .036, .043), iron, cutaway_objects)
box('Cutaway fixed nut mounting foot', (nut_x, 0, .028), (.055, .056, .009), dark, cutaway_objects)
# Nut stays fixed. Screw and pressure collar translate with the moving assembly.
shaft = rod('Screw core', (-.134, 0, axis_z), (.115, 0, axis_z), .0066, steel, rotating)
points=[]
for i in range(3600):
    x=-.130+.235*i/3599
    a=2*math.pi*x/p['lead_m']
    points.append((x, .0074*math.cos(a), axis_z+.0074*math.sin(a)))
tube('Continuous single start helical thread', points, .001, steel, rotating)
# Hub protrudes beyond the front; the screw bearing collar visibly belongs to the slide.
rod('Moving slide front bearing', (.027, 0, axis_z), (.046, 0, axis_z), .017, steel, moving)
rod('Handle boss', (.108, 0, axis_z), (.129, 0, axis_z), .013, dark, rotating)
rod('Handle hub steel cap', (.129, 0, axis_z), (.134, 0, axis_z), .014, steel, rotating)
r=p['handle_radius_m']
rod('Sliding T handle', (.120,-r,axis_z), (.120,r,axis_z), .0036, steel, rotating)
for sign in (-1,1):
    sphere('Rounded T handle end', (.120,sign*r,axis_z), .0075, steel, rotating)
tube('Screw rotation witness mark',[(.098,-.002,axis_z+.0067),(.105,-.002,axis_z+.0067)],
     .0007,brass,rotating)
for x in (.048,.052):
    rod('Front bearing trim ring',(x,0,axis_z),(x+.0014,0,axis_z),.014,steel,moving)
# Group objects around screw axis while preserving the constructed world positions.
bpy.ops.object.empty_add(location=(0,0,axis_z))
rotor=bpy.context.object
rotor.name='Rotating screw assembly'
for o in rotating:
    o.parent=rotor
    o.location.z-=axis_z
# Cyan vector terminates at the hand contact point (tangent to the handle).
rod('Hand force vector', (.12,r,axis_z-.042), (.12,r,axis_z-.010), .0018, cyan, force_objects)
rod('Hand force arrowhead', (.12,r,axis_z-.010), (.12,r,axis_z), .006, cyan, force_objects, cone=True)
for o in force_objects:
    o.parent=rotor
    o.location.z-=axis_z
# Torque arc lies in the plane normal to the screw axis.
arc_points=[]
for i in range(55):
    a=-.7+2.0*i/54
    arc_points.append((.139, .035*math.cos(a), axis_z+.035*math.sin(a)))
tube('Torque direction arc', arc_points, .0015, cyan, force_objects)
last=Vector(arc_points[-1]); tangent=Vector((0,-math.sin(1.3),math.cos(1.3)))
rod('Torque arc arrow', last, last+.010*tangent, .0045, cyan, force_objects, cone=True)
# Isolate the internals in the cutaway; all other shots retain the full object.
static_outer=[o for o in bpy.context.scene.objects if o.type in {'MESH','CURVE','FONT'}
              and o not in moving+rotating+force_objects+cutaway_objects]
# Store local baselines for translation, and animate visibility for the cutaway.
baselines={o: o.location.copy() for o in moving}
for f in range(1,s.frame_end+1):
    t=(f-1)/s.render.fps
    angle, advance=motion(episode_progress(t,cfg),p)
    rotor.location.x=-advance
    rotor.rotation_euler.x=angle
    rotor.keyframe_insert(data_path='location',frame=f)
    rotor.keyframe_insert(data_path='rotation_euler',frame=f)
    for o in moving:
        o.location=baselines[o]-Vector((advance,0,0))
        o.keyframe_insert(data_path='location',frame=f)
    shot=next(sh for sh in cfg['shots'] if sh['start']<=t<sh['end'])
    cutaway=shot['id']=='thread'
    for o in static_outer+moving:
        # Keep the two steel grip faces and front jaw visible in other scenes.
        o.hide_render=cutaway or (shot['id']=='texture' and not o.name.startswith(
            ('Fixed grip','Fixed diagonal','Fixed jaw plate','Fixed screw head',
             'Fixed replaceable','Fixed jaw head')))
        o.keyframe_insert(data_path='hide_render',frame=f)
    for o in rotating:
        o.hide_render=shot['id']=='texture'
        o.keyframe_insert(data_path='hide_render',frame=f)
    for o in cutaway_objects:
        o.hide_render=not cutaway
        o.keyframe_insert(data_path='hide_render',frame=f)
    for o in force_objects:
        o.hide_render=shot['id']!='handle' or cfg.get('annotation_style')=='flat'
        o.keyframe_insert(data_path='hide_render',frame=f)
# Perspective cameras with per-frame eased orbit, target tracking and substantial push-ins.
for sh in cfg['shots']:
    bpy.ops.object.camera_add(location=sh['camera'])
    cam=bpy.context.object
    cam.name='CAM '+sh['id']
    cam.data.type='PERSP'
    cam.data.sensor_fit='VERTICAL'
    cam.data.sensor_height=36
    cam.data.lens=50
    cam.data.clip_start=.001
    first=round(sh['start']*s.render.fps)+1
    last=round(sh['end']*s.render.fps)
    for frame in range(first,last+1):
        u=(frame-first)/max(1,last-first)
        position,target,_=camera_pose(sh,u)
        cam.location=position
        cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
        cam.keyframe_insert(data_path='location',frame=frame)
        cam.keyframe_insert(data_path='rotation_euler',frame=frame)
    marker=s.timeline_markers.new(sh['id'],frame=first)
    marker.camera=cam
    if sh==cfg['shots'][0]:
        s.camera=cam
s['storyboard_json']=json.dumps(cfg['shots'])
s['contact_time']=cfg['contact_time']
# Every-frame kinematics must remain linear, not spline overshoot near contact.
for o in bpy.data.objects:
    if o.animation_data and o.animation_data.action:
        for fc in o.animation_data.action.fcurves:
            for key in fc.keyframe_points:
                key.interpolation='CONSTANT' if fc.data_path=='hide_render' else 'LINEAR'
s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'))
if args.stills:
    (out/'stills').mkdir(exist_ok=True)
    for sh in cfg['shots']:
        s.frame_set(round((sh['start']+sh['end'])/2*s.render.fps)+1)
        s.render.filepath=str(out/'stills'/sh['id'])+'.png'
        bpy.ops.render.render(write_still=True)
else:
    bpy.ops.render.render(animation=True)
