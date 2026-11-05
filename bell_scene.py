"""Procedural classic make-and-break bell; projected annotations are separate."""
import argparse
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0,str(Path(__file__).parent))
from bell_physics import prepare,display_state
from camera_motion import camera_pose
from blender_primitives import material,box,rod,set_rod,sphere,tube,finish

p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--output',required=True)
p.add_argument('--preview',action='store_true');p.add_argument('--stills',action='store_true');p.add_argument('--build-only',action='store_true')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);c=json.loads(Path(a.config).read_text());out=Path(a.output)
out.mkdir(parents=True,exist_ok=True);(out/'frames').mkdir(exist_ok=True)
prepared=prepare(c)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.render_aa=c.get('render_aa','FXAA')
s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True
s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.background_type='WORLD'
s.world.color=(.018,.027,.043);s.view_settings.view_transform='Standard'
preset=c['preview'] if a.preview else c
s.render.resolution_x=preset['width'];s.render.resolution_y=preset['height'];s.render.resolution_percentage=100
s.render.fps=preset['fps'];s.frame_end=round(c['duration']*s.render.fps)
s.render.image_settings.file_format='PNG';s.render.image_settings.compression=c.get('png_compression',0)
s.render.filepath=str(out/'frames')+'/'
steel=material('Brushed steel',(.55,.63,.69),.85);dark=material('Insulating mounts',(.04,.07,.09))
base=material('Dark blue panel',(.06,.12,.17));gold=material('Brass gong',(.85,.54,.17),.9)
copper=material('Enamelled copper',(.65,.22,.075),.7);red=material('Button red',(.68,.09,.07))
wire=material('Wire insulation',(.16,.20,.23));teal=material('Magnetic field schematic',(.05,.70,.65))
white=material('Circuit terminals',(.78,.84,.86));ivory=material('Battery casing',(.61,.70,.73))
box('Mounting backplate',(0,.052,.129),(.30,.012,.25),base,bevel=.006)
box('Base foot',(0,.015,.006),(.32,.14,.012),dark,bevel=.004)
for x in (-.135,.135):
 for z in (.020,.236):rod('Panel bolt',(x,.039,z),(x,.046,z),.004,steel,vertices=6)
# Gong is a spherical cap facing the viewer (-Y), with a real rim and central fixing.
cx,cy,cz=.075,.018,.175;R=.062;segments=72;rings=25
verts=[(cx,cy-R,cz)];faces=[]
for j in range(1,rings+1):
 theta=math.radians(85)*j/rings
 for k in range(segments):
  phi=2*math.pi*k/segments
  verts.append((cx+R*math.sin(theta)*math.cos(phi),cy-R*math.cos(theta),cz+R*math.sin(theta)*math.sin(phi)))
for k in range(segments):faces.append((0,1+k,1+(k+1)%segments))
for j in range(rings-1):
 for k in range(segments):
  i=1+j*segments+k;n=1+j*segments+(k+1)%segments
  faces.append((i,i+segments,n+segments,n))
mesh=bpy.data.meshes.new('Spun brass dome');mesh.from_pydata(verts,[],faces)
gong=bpy.data.objects.new('Bell gong',mesh);bpy.context.collection.objects.link(gong);finish(gong,gong.name,gold)
for f in mesh.polygons:f.use_smooth=True
rim=[(cx+R*math.sin(math.radians(85))*math.cos(2*math.pi*i/100),cy-R*math.cos(math.radians(85)),cz+R*math.sin(math.radians(85))*math.sin(2*math.pi*i/100)) for i in range(101)]
tube('Rolled gong rim',rim,.0014,gold)
rod('Gong fixing',(cx,cy-R-.006,cz),(cx,cy-R+.001,cz),.005,steel,vertices=12)
rod('Gong rear mounting post',(cx,.030,cz),(cx,.047,cz),.010,dark)
# Fixed solenoid, bobbin and pole, aligned with the translating armature.
yc=.005;zc=.078
rod('Iron pole',(-.0585,yc,zc),(.014,yc,zc),.006,steel)
rod('Coil bobbin',(-.052,yc,zc),(.002,yc,zc),.014,dark)
for x in (-.053,.003):rod('Bobbin flange',(x-.001,yc,zc),(x+.001,yc,zc),.021,dark)
helix=[]
for i in range(1100):
 angle=-math.pi/2+2*math.pi*24*i/1099
 helix.append((-.050+.050*i/1099,yc+.017*math.cos(angle),zc+.017*math.sin(angle)))
tube('Copper coil windings',helix,.00105,copper)
box('Coil mount',(-.022,.035,.068),(.058,.024,.035),dark,bevel=.002)
# Moving plate, linked hammer and spring.
bpy.ops.object.empty_add();arm=bpy.context.object;arm.name='Armature assembly'
box('Iron armature',(-.066,yc,zc),(.003,.042,.044),steel,arm)
box('Armature guide',(-.066,.034,zc),(.004,.018,.018),dark,arm)
ball_r=.006
hit_center_x=cx-math.sqrt((R+ball_r)**2-(cy-.007)**2)
ball_start_x=hit_center_x-c['physics']['stroke_m']
rod('Hammer stem',(-.066,yc,.094),(ball_start_x,.007,.175),.0017,steel,arm)
sphere('Hammer ball',(ball_start_x,.007,.175),ball_r,steel,arm)
anchor=-.120;rest_length=-.0675-anchor
box('Spring anchor',(-.121,.016,zc),(.008,.035,.016),dark)
spring_points=[(0,0,0)]
for j in range(160):
 u=j/159;ang=2*math.pi*8*u
 spring_points.append((rest_length*(.08+.84*u),.003*math.cos(ang),.003*math.sin(ang)))
spring_points.append((rest_length,0,0))
spring=tube('Return spring',spring_points,.00055,steel);spring.location=(anchor,yc,zc)
# Contact screw on an insulating support. The finger flexes while closed.
box('Contact insulating mount',(-.110,.024,.112),(.030,.018,.019),dark)
rod('Adjusting contact screw',(-.124,-.020,.112),(-.0945,-.020,.112),.0024,steel)
rod('Screw adjustment head',(-.128,-.020,.112),(-.124,-.020,.112),.004,steel,vertices=10)
fixed=box('Fixed contact',(-.09325,-.020,.112),(.0025,.009,.008),gold,bevel=.0004)
moving=box('Moving contact',(-.09075,-.020,.112),(.0025,.009,.008),gold,bevel=.0004)
leaf=rod('Flexible contact finger',(-.066,-.019,.091),(-.09075,-.020,.112),.00115,copper)
# Battery and held pushbutton; wiring is one series circuit, not a second source.
box('6 V battery',(-.104,-.007,.033),(.056,.028,.030),ivory,bevel=.003)
for x in (-.125,-.083):rod('Battery terminal',(x,-.013,.048),(x,-.013,.054),.003,gold)
box('Button base',(.094,-.008,.031),(.042,.033,.022),dark,bevel=.003)
rod('Pushbutton bezel',(.094,-.027,.031),(.094,-.021,.031),.012,steel)
rod('Held pushbutton',(.094,-.031,.031),(.094,-.027,.031),.009,red)
paths=[
 [(-.083,-.014,.052),(-.076,-.027,.023),(.071,-.027,.023),(.080,-.023,.031)],
 [(.108,-.023,.031),(.125,-.015,.048),(.115,-.012,.057),(.000,yc,.061)],
 [(-.050,yc,.061),(-.113,.010,.048),(-.134,-.002,.062),(-.134,-.010,.112),(-.124,-.020,.112)],
 [(-.066,-.019,.065),(-.075,-.030,.046),(-.128,-.029,.046),(-.125,-.014,.052)]]
for n,path in enumerate(paths):tube('Insulated circuit wire '+str(n),path,.0017,wire)
for xyz in [paths[0][0],paths[1][-1],paths[2][0],paths[2][-1],paths[3][-1]]:sphere('Screw terminal',xyz,.0025,gold)
# Schematic magnetic flux loops; intensity tracks modeled current, with no Tesla scale.
field_paths=[]
for height in (.024,.032,.040):
 points=[]
 # Inside branch traverses the core; the outer return branch loops above/below it.
 for j in range(15):points.append((.014-.075*j/14,yc,zc))
 for j in range(80):
  u=j/79;xx=-.061+.075*u;zz=zc+height*math.sin(math.pi*u)
  points.append((xx,yc,zz))
 points.append((.014,yc,zc))
 field_paths.append(points)
# Store state once; the geometry, overlays, current cues and audio share this timeline.
states=[]
for frame in range(1,s.frame_end+1):
 t=(frame-1)/s.render.fps;st=display_state(t,c,prepared);states.append(st)
 x=st['x'];arm.location.x=x;arm.keyframe_insert(data_path='location',frame=frame)
 spring.scale.x=(rest_length+x)/rest_length;spring.keyframe_insert(data_path='scale',frame=frame)
 gap=max(.0003,.6*(x-c['physics']['close_at_m'])) if not st['closed'] else 0
 moving.location.x=-.09075+gap;moving.keyframe_insert(data_path='location',frame=frame)
 set_rod(leaf,(-.066+x,-.019,.091),(moving.location.x,-.020,.112))
 for key in ('location','rotation_euler','scale'):leaf.keyframe_insert(data_path=key,frame=frame)
 intensity=min(1,st['current']/.5)
 teal.diffuse_color=(.02+.03*intensity,.10+.70*intensity,.12+.62*intensity,1)
 teal.keyframe_insert(data_path='diffuse_color',frame=frame)
for sh in c['shots']:
 bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='CAM '+sh['id'];cam.data.type='PERSP'
 cam.data.sensor_fit='VERTICAL';cam.data.sensor_height=36;cam.data.lens=50;cam.data.clip_start=.001
 first=round(sh['start']*s.render.fps)+1;last=round(sh['end']*s.render.fps)
 for f in range(first,last+1):
  xyz,target,_=camera_pose(sh,(f-first)/max(1,last-first));cam.location=xyz
  cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
  cam.keyframe_insert(data_path='location',frame=f);cam.keyframe_insert(data_path='rotation_euler',frame=f)
 marker=s.timeline_markers.new(sh['id'],frame=first);marker.camera=cam
 if sh==c['shots'][0]:s.camera=cam
for o in list(bpy.data.objects)+[teal]:
 if o.animation_data and o.animation_data.action:
  for fc in o.animation_data.action.fcurves:
   for key in fc.keyframe_points:key.interpolation='CONSTANT' if fc.data_path=='hide_render' else 'LINEAR'
s['bell_config']=json.dumps(c);s['hammer_start_x']=ball_start_x;s['gong_radius']=R;s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'))
w=s.render.resolution_x;h=s.render.resolution_y;rows=[]
for idx,st in enumerate(states):
 f=idx+1;s.frame_set(f);x=st['x']
 def project(xyz):
  uv=world_to_camera_view(s,s.camera,Vector(xyz));return [uv.x*w,(1-uv.y)*h]
 projection=s.camera.calc_matrix_camera(bpy.context.evaluated_depsgraph_get(),x=w,y=h) @ s.camera.matrix_world.inverted()
 row=dict(st,frame=f,t=idx/s.render.fps,view_projection=[list(v) for v in projection],armature=project((-.066+x,-.019,zc)),
   mag_direction=project((-.046+x,-.019,zc)),spring_direction=project((-.086+x,-.019,zc)),
   contact=project((moving.location.x,-.025,.112)),fixed_contact=project((-.092,-.025,.112)),
   hammer=project((ball_start_x+x,.007,.175)),button=project((.094,-.035,.031)),
   wires=[[project(pt) for pt in path] for path in paths])
 rows.append(row)
(out/'bell-anchors.json').write_text(json.dumps({'width':w,'height':h,'fps':s.render.fps,'frames':rows,'physical_events':prepared[1],'field_paths':field_paths},indent=2)+'\n')
if a.stills:
 (out/'stills').mkdir(exist_ok=True)
 for sh in c['shots']:
  s.frame_set(round((sh['start']+sh['end'])/2*s.render.fps)+1);s.render.filepath=str(out/'stills'/sh['id'])+'.png'
  bpy.ops.render.render(write_still=True)
elif not a.build_only:
 s.frame_set(1);s.render.filepath=str(out/'frames')+'/';bpy.ops.render.render(animation=True)
