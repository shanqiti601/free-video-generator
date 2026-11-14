import bpy, math, os
from mathutils import Vector
# FACT BITES UNBOXED — genuine procedural 3D mechanism pilot
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for d in bpy.data.materials: bpy.data.materials.remove(d)
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items.keys() else 'BLENDER_EEVEE'
scene.render.resolution_x=540; scene.render.resolution_y=960; scene.render.resolution_percentage=100
scene.render.fps=18; scene.frame_start=1; scene.frame_end=144
scene.render.image_settings.file_format='FFMPEG'; scene.render.ffmpeg.format='MPEG4'; scene.render.ffmpeg.codec='H264'; scene.render.ffmpeg.constant_rate_factor='HIGH'; scene.render.filepath=os.path.abspath('output/unboxed/BLENDER-3D-PILOT.mp4')
scene.render.image_settings.color_mode='RGB'
scene.render.film_transparent=False
scene.world.color=(0.018,0.025,0.045)
scene.view_settings.view_transform='AgX'
def mat(name,color,metal=0,rough=.35,alpha=1):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,alpha); m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,alpha); bs.inputs['Metallic'].default_value=metal; bs.inputs['Roughness'].default_value=rough
 if alpha<1: bs.inputs['Alpha'].default_value=alpha
 return m
blue=mat('Deep cobalt lacquer',(0.018,.12,.48),.72,.22)
steel=mat('Brushed precision steel',(.48,.58,.7),.88,.24)
gold=mat('Warm brass',(.72,.38,.08),.78,.25)
ink=mat('Saturated blue ink',(.005,.08,.8),.12,.18)
glass=mat('Translucent reservoir',(.35,.68,.9),.25,.18,.28)
dark=mat('Graphite',(.012,.018,.03),.25,.3)
white=mat('Soft white',(.82,.9,1),.05,.35)
def cyl(name,r,depth,loc,material,vertices=64,bevel=.025):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=r, depth=depth, location=loc)
 o=bpy.context.object;o.name=name;o.data.materials.append(material)
 if bevel:
  mod=o.modifiers.new('Machined edge highlights','BEVEL');mod.width=bevel;mod.segments=3
  o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
 return o
def sphere(name,r,loc,material):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=r, location=loc)
 o=bpy.context.object;o.name=name;o.data.materials.append(material); bpy.ops.object.shade_smooth();return o
def key_move(o, start, end, f1=1, f2=72):
 o.location=start;o.keyframe_insert(data_path='location',frame=f1)
 o.location=end;o.keyframe_insert(data_path='location',frame=f2)
# Pen components are aligned on Z; exploded assembly closes into a complete pen.
barrel=cyl('01 — Outer pen barrel',.24,3.6,(0,0,1.8),blue,96,.06)
# barrel visual cutaway: long clear side window strip on front
window=cyl('Cutaway inspection window',.245,2.25,(0,-.012,1.82),glass,96,.012)
# cap and click button
cap=cyl('Rear click housing',.255,.46,(0,0,3.83),dark,96,.045)
button=cyl('Click button',.16,.16,(0,0,4.14),gold,64,.025)
# tip assembly and small writing ball
tip=cyl('Tapered metal nose',.17,.55,(0,0,-.23),steel,64,.04)
ball=sphere('Rotating ballpoint tip',.075,(0,0,-.55),steel)
socket=cyl('Ball retaining socket',.105,.15,(0,0,-.43),gold,64,.018)
# ink tube, inner ink core and spring
reservoir=cyl('Transparent ink reservoir',.095,2.45,(0,0,1.55),glass,48,.018)
inkcore=cyl('Visible blue ink column',.061,1.95,(0,0,1.48),ink,48,.01)
# spring as a bevelled 3D curve helix
cu=bpy.data.curves.new('Compression spring geometry','CURVE');cu.dimensions='3D';cu.bevel_depth=.025;cu.bevel_resolution=3
sp=cu.splines.new('POLY'); pts=180;sp.points.add(pts-1)
for i in range(pts):
 t=i/(pts-1);a=t*math.pi*2*12
 sp.points[i].co=(.13*math.cos(a),.13*math.sin(a),.55+t*.8,1)
spring=bpy.data.objects.new('Stainless compression spring',cu);bpy.context.collection.objects.link(spring);spring.data.materials.append(steel)
# floating ink bead at the ball, subtle and illustrative
drop=sphere('Ink transfer bead',.045,(0,0,-.68),ink)
# exploded arrangement: reservoir and spring rise; nose and ball descend, then components assemble
for obj,st,en in [
 (reservoir,(0,0,2.45),(0,0,1.55)),(inkcore,(0,0,2.4),(0,0,1.48)),
 (spring,(0,0,3.45),(0,0,.95)),(tip,(0,0,-.9),(0,0,-.23)),
 (socket,(0,0,-.85),(0,0,-.43)),(ball,(0,0,-1.1),(0,0,-.55))]:
 key_move(obj,st,en,1,72)
# barrel reveal: fades not required; hold central while parts animate
# typography in-scene, kept away from safe edges
def txt(body,loc,size,material,name):
 cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.size=size;cu.extrude=.001
 ob=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(math.radians(90),0,0);ob.data.materials.append(material);return ob
txt('INSIDE A BALLPOINT PEN',(-1.35,-.65,4.85),.19,white,'Title')
txt('BALL  •  SOCKET  •  INK RESERVOIR',(-1.35,-.65,-1.35),.105,white,'Mechanism caption')
# floor and studio lighting
cyl('Studio plinth',2.7,.12,(0,0,-1.75),dark,96,.08)
def area(name,loc,power,color,size,target):
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.name=name;l.data.energy=power;l.data.color=color;l.data.shape='DISK';l.data.size=size;l.rotation_euler=(Vector(target)-l.location).to_track_quat('-Z','Y').to_euler()
area('Large cool key', (4,-5,6),1100,(.55,.72,1),5,(0,0,1))
area('Warm rim',(-4,1,3),950,(1,.48,.2),4,(0,0,1))
area('Front fill',(0,-4,0),650,(.35,.55,1),3,(0,0,1))
# camera, slight animated orbit and close-up perspective
bpy.ops.object.camera_add(location=(5,-9,2.2));cam=bpy.context.object;cam.name='Cinematic product camera';cam.data.type='ORTHO';cam.data.ortho_scale=7.8
target=Vector((0,0,1.3));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();scene.camera=cam
cam.keyframe_insert(data_path='location',frame=1);cam.location=(4.1,-9.5,1.8);cam.keyframe_insert(data_path='location',frame=144)
cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.keyframe_insert(data_path='rotation_euler',frame=144)
# animate final assembled reveal: hold exploded, assemble, then hold
for obj in [reservoir,inkcore,spring,tip,socket,ball]:
 obj.keyframe_insert(data_path='location',frame=108)
# smooth interpolation
for ob in scene.objects:
 if ob.animation_data and ob.animation_data.action:
  for fc in ob.animation_data.action.fcurves:
   for kp in fc.keyframe_points: kp.interpolation='BEZIER'
scene.frame_set(1)
os.makedirs('output/unboxed',exist_ok=True)
scene.render.filepath=os.path.abspath('output/unboxed/BLENDER-3D-PILOT.mp4')
bpy.ops.render.render(animation=True)
print('BLENDER_3D_RENDER_OK',scene.render.resolution_x,scene.render.resolution_y,scene.frame_end)
