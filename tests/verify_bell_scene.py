"""Baked bell geometry: no 3D scientific graphics, valid gaps and strikes."""
import bpy
import json
import math
from mathutils import Vector
s=bpy.context.scene;c=json.loads(s['bell_config'])
assert not any(o.name.startswith('Schematic magnetic flux') for o in s.objects)
assert not any('force arrow' in o.name.lower() for o in s.objects)
arm=bpy.data.objects['Armature assembly'];fixed=bpy.data.objects['Fixed contact'];moving=bpy.data.objects['Moving contact']
ball=bpy.data.objects['Hammer ball'];spring=bpy.data.objects['Return spring']
min_dist=99
for f in range(1,s.frame_end+1,7):
 s.frame_set(f);bpy.context.view_layer.update()
 x=arm.location.x
 assert -.0000001<=x<=c['physics']['stroke_m']+1e-7
 pole_gap=.006-x
 assert pole_gap>=.0025-1e-7
 # Closed contacts may touch, never interpenetrate.
 assert moving.location.x-.00125>=fixed.location.x+.00125-1e-7
 pos=ball.matrix_world.translation;distance=(pos-Vector((.075,.018,.175))).length
 assert distance>=.068-2e-7
 min_dist=min(min_dist,distance)
 assert abs(spring.scale.x-(.0525+x)/.0525)<1e-6
assert min_dist<.06805
for sh in c['shots']:
 s.frame_set(round(sh['start']*s.render.fps)+1)
 assert s.camera.name=='CAM '+sh['id']
print('PASS: no 3D annotation meshes, pole gap positive, no contact/gong penetration, spring attachment and eight camera cuts')
