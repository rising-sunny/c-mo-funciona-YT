"""Artifact integration check; run with Blender --background <scene.blend> --python this_file."""
import bpy
import json
s = bpy.context.scene
fixed = bpy.data.objects['Fixed replaceable steel jaw']
mobile = bpy.data.objects['Moving replaceable steel jaw']
piece = bpy.data.objects['Copper coloured workpiece']


def bounds(obj):
    return [min((obj.matrix_world @ __import__('mathutils').Vector(p)).x for p in obj.bound_box),
            max((obj.matrix_world @ __import__('mathutils').Vector(p)).x for p in obj.bound_box)]


previous = 1
for t in (0, 4, 9, 14, 18.9, 19, 21.9):
    s.frame_set(round(t*s.render.fps)+1)
    bpy.context.view_layer.update()
    gap = bounds(mobile)[0]-bounds(piece)[1]
    assert gap >= -1e-6, f'Jaw penetrates workpiece at {t}s: {gap}'
    assert gap <= previous+1e-6, f'Jaw opens unexpectedly at {t}s'
    assert abs(bounds(fixed)[1]-bounds(piece)[0]) < 1e-6
    previous = gap
assert abs(previous) < 1e-6, f'Jaw never reaches first contact: {previous}'
for shot in json.loads(s['storyboard_json']):
    t=shot['start']
    camera=shot['id']
    s.frame_set(round(t*s.render.fps)+1)
    assert s.camera.name == 'CAM '+camera, f'Wrong camera at {t}s: {s.camera.name}'
    assert s.camera.data.type == 'PERSP'
    nut = bpy.data.objects['Stationary bronze threaded nut']
    assert nut.hide_render == (camera != 'thread')
    start_position=s.camera.location.copy()
    s.frame_set(round(shot['end']*s.render.fps))
    assert (s.camera.location-start_position).length > .015, f'Static camera in {camera}'
print('PASS: baked jaw contact, no penetration, perspective camera motion and cutaway visibility')
