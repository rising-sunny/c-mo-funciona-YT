"""Two connected syringe cutaways with volume-conserving kinematics. Blender 4.3+."""
import argparse
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0,str(Path(__file__).parent))
from camera_motion import camera_pose
from hydraulics import state,quantities

p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--output',required=True)
p.add_argument('--preview',action='store_true');p.add_argument('--stills',action='store_true');p.add_argument('--build-only',action='store_true')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);c=json.loads(Path(a.config).read_text());out=Path(a.output)
out.mkdir(parents=True,exist_ok=True);(out/'frames').mkdir(exist_ok=True)
pv=c['physics'];q=quantities(pv)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.render_aa=c.get('render_aa','FXAA')
s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True
s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.background_type='WORLD'
s.world.color=(.018,.027,.043);s.view_settings.view_transform='Standard'
preset=c['preview'] if a.preview else c
s.render.resolution_x=preset['width'];s.render.resolution_y=preset['height'];s.render.resolution_percentage=100
s.render.fps=preset['fps'];s.frame_end=round(c['duration']*s.render.fps);s.render.image_settings.file_format='PNG'
s.render.image_settings.compression=c.get('png_compression',0)
s.render.filepath=str(out/'frames')+'/'


def mat(name,rgb):
 m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);return m

shell=mat('Ivory polymer barrel',(.72,.80,.84));steel=mat('Polished guide metal',(.55,.65,.72))
dark=mat('Seal rubber',(.035,.06,.08));base=mat('Laboratory base',(.075,.12,.16))
water=mat('Air free hydraulic liquid',(.03,.56,.78));gold=mat('Output piston accent',(.98,.62,.16))
cyan=mat('Input piston accent',(.12,.88,.82));ink=mat('Graduation ink',(.09,.20,.25))


def finish(o,name,m,parent=None):
 o.name=name;o.data.materials.append(m)
 if parent:o.parent=parent
 return o


def box(name,xyz,dims,m,parent=None,bevel=.001):
 bpy.ops.mesh.primitive_cube_add(size=1,location=xyz);o=bpy.context.object;o.dimensions=dims
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  b=o.modifiers.new('Rounded edges','BEVEL');b.width=bevel;b.segments=3
  o.modifiers.new('Normals','WEIGHTED_NORMAL')
 return finish(o,name,m,parent)


def cylinder(name,xyz,r,depth,m,parent=None):
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=r,depth=depth,location=xyz)
 o=bpy.context.object
 for poly in o.data.polygons:
  if len(poly.vertices)==4:poly.use_smooth=True
 return finish(o,name,m,parent)


def ring(name,xyz,r,m,parent=None,thickness=.0015):
 bpy.ops.mesh.primitive_torus_add(major_radius=r,minor_radius=thickness,major_segments=48,minor_segments=10,location=xyz)
 return finish(bpy.context.object,name,m,parent)


def tube(name,points,r,m):
 cv=bpy.data.curves.new(name,'CURVE');cv.dimensions='3D';cv.bevel_depth=r;cv.bevel_resolution=3
 sp=cv.splines.new('POLY');sp.points.add(len(points)-1)
 for pt,co in zip(sp.points,points):pt.co=(*co,1)
 o=bpy.data.objects.new(name,cv);bpy.context.collection.objects.link(o);return finish(o,name,m)


def barrel(name,x,r):
 # Open front sector reveals the fluid and piston without transparency sorting artifacts.
 verts=[];faces=[];n=66
 for z,rad in [(.025,r+.0006),(.160,r+.0006),(.025,r+.0024),(.160,r+.0024)]:
  for i in range(n):
   theta=math.radians(-15+210*i/(n-1));verts.append((x+rad*math.cos(theta),rad*math.sin(theta),z))
 for i in range(n-1):
  j=i+1
  faces.extend([(i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),
                (i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)])
 faces.extend([(0,n,3*n,2*n),(n-1,3*n-1,4*n-1,2*n-1)])
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o)
 finish(o,name,shell)
 ring(name+' top lip',(x,0,.16),r+.001,shell)
 ring(name+' base seal',(x,0,.025),r+.001,steel)
 cylinder(name+' bottom cap',(x,0,.022),r+.003,.006,shell)
 box(name+' finger flange',(x,0,.158),(2*r+.031,.014,.004),shell)
 for j in range(12):
  z=.035+j*.01
  box(name+' graduation',(x+r+.002,-.002,z),(.006 if j%5==0 else .003,.0012,.0006),ink,bevel=0)


box('Laboratory platform',(0,0,.004),(.27,.15,.008),base,bevel=.004)
for x in (-.115,.115):
 for y in (-.056,.056):cylinder('Mounting bolt',(x,y,.009),.004,.002,steel)
xs=[-.085,.085];rs=[math.sqrt(pv['input_area_m2']/math.pi),math.sqrt(pv['output_area_m2']/math.pi)]
parents=[];fluids=[]
for i,(x,r,z,accent) in enumerate(zip(xs,rs,[.14,.065],[cyan,gold])):
 name='Small' if i==0 else 'Large'
 barrel(name+' barrel',x,r)
 bpy.ops.object.empty_add(location=(0,0,0));parent=bpy.context.object;parent.name=name+' plunger assembly';parents.append(parent)
 cylinder(name+' piston seal',(x,0,z),r+.0003,.005,dark,parent)
 cylinder(name+' coloured piston face',(x,0,z+.0026),r*.88,.001,accent,parent)
 ring(name+' rubber piston lip',(x,0,z-.0009),r,dark,parent,thickness=.0008)
 cylinder(name+' plunger rod',(x,0,z+.055),.0038 if i==0 else .005,.11,steel,parent)
 box(name+' thumb pad',(x,0,z+.11),(2*r+.012,.032,.008),shell,parent,bevel=.003)
 cylinder(name+' fluid',(x,0,.025+(z-.0025-.025)/2),1,1,water)
 fluid=bpy.context.object;fluid.scale=(r,r,z-.0025-.025);fluids.append(fluid)
 cylinder(name+' nozzle',(x,0,.016),.006,.016,shell)
 cylinder(name+' fluid nozzle',(x,-.001,.016),.0046,.017,water)
 box(name+' support',(x,.025,.017),(.038,.02,.018),base,bevel=.003)
# Weight sits on the large thumb pad and follows it; no fictitious mass value is claimed.
for j in range(3):
 box('Load plate',(xs[1],0,.184+j*.010),(.058,.041,.009),steel,parents[1],bevel=.002)
 box('Load plate groove',(xs[1],-.0208,.184+j*.010),(.040,.0006,.0015),dark,parents[1],bevel=.0002)
# Frontward U-shaped hydraulic line; its lumen is shown in blue as a cutaway.
path=[]
for i in range(12):path.append((xs[0],-.050*i/11,.014))
for i in range(50):path.append((xs[0]+.17*i/49,-.05,.014))
for i in range(12):path.append((xs[1],-.050*(1-i/11),.014))
tube('Visible hydraulic line lumen',path,.0045,water)
tube('Hydraulic hose edge highlight',[(x,y-.002,z+.0037) for x,y,z in path],.00065,shell)
# Painted flow dots on the exposed lumen: schematic direction cues, not fluid particles.
flow=[]
for i in range(6):
 o=cylinder('Schematic flow marker',path[0],.0012,.0012,shell);flow.append(o)
# Arc-length sampling allows flow cues to follow displaced volume through the same lumen.
lengths=[0]
for p0,p1 in zip(path,path[1:]):lengths.append(lengths[-1]+(Vector(p1)-Vector(p0)).length)

def along(distance):
 d=distance%lengths[-1]
 j=next((j for j in range(1,len(lengths)) if lengths[j]>=d),len(lengths)-1)
 u=(d-lengths[j-1])/max(1e-8,lengths[j]-lengths[j-1]);v=Vector(path[j-1]).lerp(Vector(path[j]),u)
 return v+Vector((0,-.004,.0015))

for frame in range(1,s.frame_end+1):
 t=(frame-1)/s.render.fps;st=state(t,pv,c['motion_start'],c['motion_end'])
 parents[0].location.z=-st['input_displacement_m'];parents[1].location.z=st['output_displacement_m']
 for parent in parents:parent.keyframe_insert(data_path='location',frame=frame)
 for i,fluid in enumerate(fluids):
  z=[.14-st['input_displacement_m'],.065+st['output_displacement_m']][i]
  height=z-.0025-.025;fluid.scale.z=height;fluid.location.z=.025+height/2
  fluid.keyframe_insert(data_path='scale',frame=frame);fluid.keyframe_insert(data_path='location',frame=frame)
 for j,o in enumerate(flow):
  o.location=along(st['transferred_volume_m3']/(math.pi*.0045**2)+j*lengths[-1]/len(flow))
  o.keyframe_insert(data_path='location',frame=frame)
for sh in c['shots']:
 bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='CAM '+sh['id'];cam.data.type='PERSP'
 cam.data.sensor_fit='VERTICAL';cam.data.sensor_height=36;cam.data.lens=50;cam.data.clip_start=.001
 first=round(sh['start']*s.render.fps)+1;last=round(sh['end']*s.render.fps)
 for frame in range(first,last+1):
  xyz,target,_=camera_pose(sh,(frame-first)/max(1,last-first));cam.location=xyz
  cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
  cam.keyframe_insert(data_path='location',frame=frame);cam.keyframe_insert(data_path='rotation_euler',frame=frame)
 marker=s.timeline_markers.new(sh['id'],frame=first);marker.camera=cam
 if sh==c['shots'][0]:s.camera=cam
for o in bpy.data.objects:
 if o.animation_data and o.animation_data.action:
  for fc in o.animation_data.action.fcurves:
   for key in fc.keyframe_points:key.interpolation='LINEAR'
s['hydraulic_config']=json.dumps(c);s['initial_piston_z']=json.dumps([.14,.065]);s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'))
# Project physically meaningful anchors for the independent 2D annotation pass.
rows=[];w=s.render.resolution_x;h=s.render.resolution_y
for f in range(1,s.frame_end+1):
 s.frame_set(f);t=(f-1)/s.render.fps;st=state(t,pv,c['motion_start'],c['motion_end'])
 z1=.14-st['input_displacement_m'];z2=.065+st['output_displacement_m']
 def project(xyz):
  uv=world_to_camera_view(s,s.camera,Vector(xyz));return [uv.x*w,(1-uv.y)*h]
 rows.append(dict(frame=f,t=t,shot=next(sh['id'] for sh in c['shots'] if sh['start']<=t<sh['end']),
   input=project((xs[0],0,z1+.114)),input_direction=project((xs[0],0,z1+.074)),
   output=project((xs[1],0,z2-.0025)),output_direction=project((xs[1],0,z2+.0375)),
   area1=project((xs[0],0,z1+.004)),area2=project((xs[1],0,z2+.004)),
   input_start=project((xs[0]-.025,0,.14)),input_end=project((xs[0]-.025,0,z1)),
   output_start=project((xs[1]+.042,0,.065)),output_end=project((xs[1]+.042,0,z2)),
   progress=st['progress']))
(out/'hydraulic-anchors.json').write_text(json.dumps({'width':w,'height':h,'fps':s.render.fps,'frames':rows},indent=2)+'\n')
if a.stills:
 (out/'stills').mkdir(exist_ok=True)
 for sh in c['shots']:
  s.frame_set(round((sh['start']+sh['end'])/2*s.render.fps)+1);s.render.filepath=str(out/'stills'/sh['id'])+'.png'
  bpy.ops.render.render(write_still=True)
elif not a.build_only:
 s.frame_set(1);s.render.filepath=str(out/'frames')+'/';bpy.ops.render.render(animation=True)
