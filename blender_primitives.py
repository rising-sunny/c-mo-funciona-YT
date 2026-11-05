"""Small shared Blender geometry helpers; evaluated only inside Blender."""
import bpy
from mathutils import Vector


def material(name,color,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.metallic=metal;m.roughness=.28 if metal else .5;return m


def finish(o,name,m,parent=None):
 o.name=name;o.data.materials.append(m)
 if parent:o.parent=parent
 return o


def box(name,xyz,dims,m,parent=None,bevel=.001):
 bpy.ops.mesh.primitive_cube_add(size=1,location=xyz);o=bpy.context.object;o.dimensions=dims
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('Machined edges','BEVEL');mod.width=bevel;mod.segments=3;o.modifiers.new('Face normals','WEIGHTED_NORMAL')
 return finish(o,name,m,parent)


def rod(name,a,b,r,m,parent=None,vertices=32):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=1);o=bpy.context.object
 for face in o.data.polygons:
  if len(face.vertices)==4:face.use_smooth=True
 set_rod(o,a,b);return finish(o,name,m,parent)


def set_rod(o,a,b):
 delta=Vector(b)-Vector(a);o.location=(Vector(a)+Vector(b))/2;o.scale.z=delta.length
 o.rotation_euler=delta.to_track_quat('Z','Y').to_euler()


def sphere(name,xyz,r,m,parent=None):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,radius=r,location=xyz);o=bpy.context.object
 for f in o.data.polygons:f.use_smooth=True
 return finish(o,name,m,parent)


def tube(name,points,r,m,parent=None):
 cv=bpy.data.curves.new(name,'CURVE');cv.dimensions='3D';cv.bevel_depth=r;cv.bevel_resolution=2
 sp=cv.splines.new('POLY');sp.points.add(len(points)-1)
 for point,xyz in zip(sp.points,points):point.co=(*xyz,1)
 o=bpy.data.objects.new(name,cv);bpy.context.collection.objects.link(o);return finish(o,name,m,parent)
