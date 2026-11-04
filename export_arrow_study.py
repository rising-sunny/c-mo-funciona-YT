"""Blender: render the handle without mesh arrows and export camera-projected anchors."""
import argparse
import json
import math
import sys
from pathlib import Path
import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

p=argparse.ArgumentParser()
p.add_argument('--output',required=True)
p.add_argument('--config',required=True)
p.add_argument('--render',action='store_true')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
c=json.loads(Path(a.config).read_text())
out=Path(a.output);(out/'clean').mkdir(parents=True,exist_ok=True)
s=bpy.context.scene
w=s.render.resolution_x;h=s.render.resolution_y;fps=s.render.fps
# Remove only the explanatory geometry. Animation on the mechanism is preserved.
for name in ['Hand force vector','Hand force arrowhead','Torque direction arc','Torque arc arrow']:
    o=bpy.data.objects[name]
    if o.animation_data: o.animation_data_clear()
    o.hide_render=True
rotor=bpy.data.objects['Rotating screw assembly']
r=c['physics']['handle_radius_m']
shot=next(x for x in c['shots'] if x['id']=='handle')
rows=[]
for frame in range(round(shot['start']*fps)+1,round(shot['end']*fps)+1):
    s.frame_set(frame);bpy.context.view_layer.update()
    def screen(point):
        uv=world_to_camera_view(s,s.camera,Vector(point))
        if uv.z <= 0: raise ValueError('Annotation behind camera')
        return [uv.x*w,(1-uv.y)*h]
    point=rotor.matrix_world @ Vector((.12,r,0))
    tangent=rotor.matrix_world @ Vector((.12,r,.04))
    center=rotor.matrix_world @ Vector((.12,0,0))
    # Fixed-space arc in a plane normal to +X. Its increasing angle denotes +X torque.
    arc=[]
    x=rotor.location.x+.15
    for i in range(80):
        theta=-1.15+2.65*i/79
        arc.append(screen((x,.043*math.cos(theta),.089+.043*math.sin(theta))))
    rows.append({'frame':frame,'t':(frame-1)/fps-shot['start'],
                 'application':screen(point),'tangent':screen(tangent),
                 'axis':screen(center),'torque_arc':arc})
    if a.render:
        s.render.filepath=str(out/'clean'/f'{frame:04}.png')
        bpy.ops.render.render(write_still=True)
(out/'anchors.json').write_text(json.dumps({'width':w,'height':h,'fps':fps,
 'start':shot['start'],'duration':shot['end']-shot['start'],'frames':rows},indent=2)+'\n')
print('Exported',len(rows),'projected annotation frames')
