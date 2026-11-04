"""Render a separate physically shaded study from the saved procedural scene."""
import argparse
import math
import sys
from pathlib import Path
import bpy
from mathutils import Vector
p=argparse.ArgumentParser()
p.add_argument('--output',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
out=Path(a.output)
out.mkdir(parents=True,exist_ok=True)
s=bpy.context.scene
s.render.engine='CYCLES'
s.cycles.device='CPU'
s.cycles.samples=128
s.cycles.use_denoising=False
s.cycles.adaptive_threshold=.035
s.cycles.max_bounces=5
s.render.resolution_x=450
s.render.resolution_y=800
s.render.resolution_percentage=100
s.view_settings.view_transform='AgX'
s.view_settings.exposure=-.5
s.world.use_nodes=True
s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.24,.30,.40,1)
s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.12
# Rebuild materials as actual surface shaders, retaining procedural colour identity.
for m in bpy.data.materials:
    base=tuple(m.diffuse_color)
    metal=m.metallic
    rough=m.roughness
    m.use_nodes=True
    nodes=m.node_tree.nodes
    nodes.clear()
    output=nodes.new('ShaderNodeOutputMaterial')
    shader=nodes.new('ShaderNodeBsdfPrincipled')
    shader.inputs['Base Color'].default_value=base
    shader.inputs['Metallic'].default_value=metal
    shader.inputs['Roughness'].default_value=rough
    m.node_tree.links.new(shader.outputs['BSDF'],output.inputs['Surface'])
    tex=nodes.new('ShaderNodeTexNoise')
    tex.inputs['Scale'].default_value=1200 if metal else 1800
    tex.inputs['Detail'].default_value=2
    coord=nodes.new('ShaderNodeTexCoord')
    m.node_tree.links.new(coord.outputs['Object'],tex.inputs['Vector'])
    bump=nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value=.12 if metal else .22
    bump.inputs['Distance'].default_value=.00005 if metal else .00012
    m.node_tree.links.new(tex.outputs['Fac'],bump.inputs['Height'])
    m.node_tree.links.new(bump.outputs['Normal'],shader.inputs['Normal'])
    if 'Enamel' in m.name:
        shader.inputs['Coat Weight'].default_value=.3
        shader.inputs['Coat Roughness'].default_value=.3
    if 'cyan' in m.name:
        shader.inputs['Emission Color'].default_value=base
        shader.inputs['Emission Strength'].default_value=.5
# Workbench top with procedural wood colour; all visuals still generated with code.
bpy.ops.mesh.primitive_cube_add(size=1,location=(-.02,0,-.019))
bench=bpy.context.object
bench.name='Physical study - hardwood workbench'
bench.dimensions=(.9,.8,.038)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
bev=bench.modifiers.new('Bench edge chamfer','BEVEL');bev.width=.004;bev.segments=3
wood=bpy.data.materials.new('Procedural stained hardwood');wood.use_nodes=True
nodes=wood.node_tree.nodes
shader=nodes.get('Principled BSDF');shader.inputs['Roughness'].default_value=.6
coord=nodes.new('ShaderNodeTexCoord');mapping=nodes.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY'
mapping.inputs[1].default_value=(4,150,8)
noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=3
ramp=nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].color=(.045,.018,.009,1)
ramp.color_ramp.elements[1].color=(.22,.10,.045,1)
wood.node_tree.links.new(coord.outputs['Generated'],mapping.inputs[0])
wood.node_tree.links.new(mapping.outputs[0],noise.inputs['Vector'])
wood.node_tree.links.new(noise.outputs['Fac'],ramp.inputs[0])
wood.node_tree.links.new(ramp.outputs[0],shader.inputs['Base Color'])
bench.data.materials.append(wood)
for name,xyz,power,size in [('Key softbox',(.10,-.22,.40),14,.28),
                           ('Fill softbox',(-.24,-.05,.24),7,.22),
                           ('Rim softbox',(.08,.22,.30),18,.18)]:
    bpy.ops.object.light_add(type='AREA',location=xyz)
    light=bpy.context.object;light.name=name
    light.data.energy=power*.1;light.data.shape='DISK';light.data.size=size
    light.rotation_euler=(Vector((-.025,0,.09))-light.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.wm.save_as_mainfile(filepath=str(out/'material_study.blend'))
for label,time in [('overview',1.8),('handle',12)]:
    s.frame_set(round(time*s.render.fps)+1)
    s.render.filepath=str(out/f'{label}.png')
    bpy.ops.render.render(write_still=True)
