"""Validate actual baked syringe geometry, independent of the kinematics evaluator."""
import bpy
import json
import math
s=bpy.context.scene
c=json.loads(s['hydraulic_config']);p=c['physics']
small=bpy.data.objects['Small plunger assembly'];large=bpy.data.objects['Large plunger assembly']
a=bpy.data.objects['Small fluid'];b=bpy.data.objects['Large fluid']
initial=None
for t in [0,4,8,12,16,20,21,27.9]:
 s.frame_set(round(t*s.render.fps)+1)
 v=math.pi*a.scale.x*a.scale.y*a.scale.z+math.pi*b.scale.x*b.scale.y*b.scale.z
 if initial is None:initial=v
 assert abs(v-initial)<1e-9,(t,v,initial)
 assert a.scale.z>0 and b.scale.z>0
 assert abs(-small.location.z*p['input_area_m2']-large.location.z*p['output_area_m2'])<1e-9
 assert abs((a.location.z+a.scale.z/2)-(.14+small.location.z-.0025))<1e-7
 assert abs((b.location.z+b.scale.z/2)-(.065+large.location.z-.0025))<1e-7
 assert .25+small.location.z-.004>.162,'Small thumb pad intersects barrel flange'
assert abs(small.location.z+.08)<1e-7
assert abs(large.location.z-.02)<1e-7
for sh in c['shots']:
 s.frame_set(round(sh['start']*s.render.fps)+1)
 assert s.camera.name=='CAM '+sh['id']
print('PASS: fluid volume conserved, pistons coupled 4:1, wet chambers, no thumb-pad collision and seven camera cuts')
