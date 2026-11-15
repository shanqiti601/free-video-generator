import bpy, math, os
from mathutils import Vector

# FACT BITES UNBOXED — 27-second procedural 3D mechanism explainer
OUT = os.path.abspath("output/unboxed")
os.makedirs(OUT, exist_ok=True)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
    for block in list(datablocks):
        if block.users == 0:
            datablocks.remove(block)

scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 64
scene.cycles.use_denoising = False
scene.render.resolution_x = 540
scene.render.resolution_y = 960
scene.render.resolution_percentage = 100
scene.render.fps = 18
scene.frame_start = 1
scene.frame_end = 486
scene.render.image_settings.file_format = "FFMPEG"
scene.render.ffmpeg.format = "MPEG4"
scene.render.ffmpeg.codec = "H264"
scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
scene.render.filepath = os.path.join(OUT, "BLENDER-3D-BASE.mp4")
scene.world.color = (0.008, 0.014, 0.03)
scene.view_settings.view_transform = "AgX"
scene.render.image_settings.color_mode = "RGB"

def material(name, color, metallic=0.0, roughness=0.3, alpha=1.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, alpha)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*color, alpha)
    bs.inputs["Metallic"].default_value = metallic
    bs.inputs["Roughness"].default_value = roughness
    bs.inputs["Alpha"].default_value = alpha
    return m

blue = material("Deep cobalt anodized alloy", (0.012, 0.075, 0.34), .78, .22)
steel = material("Satin machined stainless steel", (.48, .59, .72), .9, .2)
gold = material("Warm brass detail", (.72, .39, .09), .82, .22)
ink = material("Electric blue ink", (.008, .07, .8), .12, .17)
glass = material("Clear polymer ink tube", (.28, .58, .78), .18, .16, .22)
black = material("Graphite polymer", (.009, .014, .026), .22, .26)
white = material("Soft studio white", (.78, .87, 1.0), .05, .32)

def cylinder(name, radius, depth, loc, mat, vertices=64, bevel=.018):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)
    if bevel:
        b = o.modifiers.new("Precision edge radius", "BEVEL")
        b.width = bevel
        b.segments = 3
        o.modifiers.new("Weighted highlights", "WEIGHTED_NORMAL")
    return o

def cone(name, r1, r2, depth, loc, mat):
    bpy.ops.mesh.primitive_cone_add(vertices=96, radius1=r1, radius2=r2, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)
    b = o.modifiers.new("Turned metal edge", "BEVEL")
    b.width = .018
    b.segments = 3
    o.modifiers.new("Weighted highlights", "WEIGHTED_NORMAL")
    return o

def sphere(name, radius, loc, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=40, ring_count=24, radius=radius, location=loc)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    return o

def hollow_cutaway_barrel():
    # A real hollow shell with a front inspection opening, not an opaque cylinder.
    verts, faces = [], []
    steps = 96
    angles = [math.radians(-35 + 250*i/steps) for i in range(steps+1)]
    z0, z1, ro, ri = .42, 4.0, .255, .218
    for z, r in ((z0, ro), (z1, ro), (z0, ri), (z1, ri)):
        for a in angles:
            verts.append((r*math.cos(a), r*math.sin(a), z))
    n = len(angles)
    for i in range(steps):
        # outer, inner, and narrow cutaway boundary faces
        faces.append((i, i+1, n+i+1, n+i))
        faces.append((2*n+i, 3*n+i, 3*n+i+1, 2*n+i+1))
        faces.append((i, 2*n+i, 2*n+i+1, i+1))
        faces.append((n+i, n+i+1, 3*n+i+1, 3*n+i))
    faces.extend([(0, n, 3*n, 2*n), (steps, 2*n+steps, 3*n+steps, n+steps)])
    mesh = bpy.data.meshes.new("Open-front hollow barrel mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(blue)
    mesh.update()
    obj = bpy.data.objects.new("01 — Hollow cobalt barrel with cutaway", mesh)
    bpy.context.collection.objects.link(obj)
    bevel = obj.modifiers.new("Micro edge chamfers", "BEVEL")
    bevel.width = .012
    bevel.segments = 2
    obj.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")
    return obj

def animate_location(obj, start, end, f_start=1, f_end=235):
    obj.location = start
    obj.keyframe_insert(data_path="location", frame=f_start)
    obj.location = end
    obj.keyframe_insert(data_path="location", frame=f_end)
    obj.keyframe_insert(data_path="location", frame=486)

# Main housing and upper clicker
barrel = hollow_cutaway_barrel()
grip = cylinder("Lower grip ring", .259, .16, (0,0,.56), black, 96, .025)
ring1 = cylinder("Brass trim ring", .261, .055, (0,0,3.91), gold, 96, .012)
cap = cylinder("Click mechanism housing", .25, .43, (0,0,4.16), black, 96, .035)
button = cylinder("Spring-loaded click button", .145, .16, (0,0,4.46), gold, 64, .025)
button_top = cylinder("Button crown", .12, .035, (0,0,4.56), steel, 64, .012)

# Internal ink cartridge and blue ink core
reservoir = cylinder("Transparent ink reservoir", .105, 2.62, (0,0,2.12), glass, 64, .012)
ink_core = cylinder("Visible ink column", .067, 2.22, (0,0,2.04), ink, 48, .009)
rear_plug = cylinder("Cartridge rear seal", .11, .13, (0,0,3.49), steel, 48, .012)

# Spring is a true 3D helix
curve = bpy.data.curves.new("Compression spring helix geometry", "CURVE")
curve.dimensions = "3D"
curve.bevel_depth = .022
curve.bevel_resolution = 4
spline = curve.splines.new("POLY")
count = 220
spline.points.add(count-1)
for i in range(count):
    t = i/(count-1)
    a = t*math.tau*11
    spline.points[i].co = (.125*math.cos(a), .125*math.sin(a), .18 + .78*t, 1)
spring = bpy.data.objects.new("Stainless click-return spring", curve)
bpy.context.collection.objects.link(spring)
spring.data.materials.append(steel)

# Nose cone, retaining socket and writing ball
nose = cone("Turned steel nose cone", .18, .055, .62, (0,0,.13), steel)
socket = cylinder("Ball retaining socket", .095, .16, (0,0,-.22), gold, 64, .012)
ball = sphere("Polished rolling ballpoint", .065, (0,0,-.34), steel)
ink_tip = sphere("Ink transfer meniscus", .027, (0,-.003,-.405), ink)

# Exploded-to-assembled movement: every part returns to its true mechanical position.
animate_location(reservoir, (0,0,5.2), (0,0,2.12))
animate_location(ink_core, (0,0,5.15), (0,0,2.04))
animate_location(rear_plug, (0,0,5.0), (0,0,3.49))
animate_location(spring, (0,0,5.4), (0,0,.58))
animate_location(nose, (0,0,-.9), (0,0,.13))
animate_location(socket, (0,0,-.95), (0,0,-.22))
animate_location(ball, (0,0,-1.0), (0,0,-.34))
animate_location(ink_tip, (0,0,-1.05), (0,-.003,-.405))

# Studio stage and soft cinematic lighting
cylinder("Floating graphite display base", 1.15, .12, (0,0,-.82), black, 96, .05)
def area_light(name, loc, power, color, size, target):
    bpy.ops.object.light_add(type="AREA", location=loc)
    l = bpy.context.object
    l.name = name
    l.data.energy = power
    l.data.color = color
    l.data.shape = "DISK"
    l.data.size = size
    l.rotation_euler = (Vector(target)-l.location).to_track_quat("-Z","Y").to_euler()
area_light("Cool key softbox", (3.5,-4.5,6), 900, (.55,.72,1), 4.0, (0,0,2))
area_light("Warm metallic rim", (-3.5,1.5,3.5), 1050, (1,.48,.2), 3.0, (0,0,2))
area_light("Front fill strip", (0,-4,1), 500, (.35,.55,1), 3.0, (0,0,2))
area_light("Top edge light", (1,2,6), 700, (.65,.78,1), 2.5, (0,0,3))

# Portrait product camera; framing leaves clean safe zones for title and subtitles.
bpy.ops.object.camera_add(location=(0,-12,2.15))
cam = bpy.context.object
cam.name = "Portrait macro product camera"
cam.data.type = "ORTHO"
cam.data.ortho_scale = 6.2
target = Vector((0,0,2.0))
cam.rotation_euler = (target-cam.location).to_track_quat("-Z","Y").to_euler()
scene.camera = cam
cam.keyframe_insert(data_path="location", frame=1)
cam.location = (.35,-11.2,2.35)
cam.rotation_euler = (Vector((0,0,2.0))-cam.location).to_track_quat("-Z","Y").to_euler()
cam.keyframe_insert(data_path="location", frame=486)
cam.keyframe_insert(data_path="rotation_euler", frame=486)

# Smooth animation curves
for obj in scene.objects:
    if obj.animation_data and obj.animation_data.action:
        for fc in obj.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"

scene.frame_set(1)
bpy.ops.render.render(animation=True)
print("FACT_BITES_3D_BASE_RENDER_OK", scene.render.resolution_x, scene.render.resolution_y, scene.frame_end)
