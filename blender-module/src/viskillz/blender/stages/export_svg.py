import os

import bpy
from viskillz.blender.common import move, rotate_global
from viskillz.blender.constants import rotation_vectors
from viskillz.blender.scene import show_object, hide_object
from viskillz.blender.stages.common import clean_and_get_shape_ids


def file_name(shape_id: str,
              rotation,
              frame: int,
              camera: int) -> str:
    return ".".join([shape_id, "".join([str(r // 90) for r in rotation]), str(frame).zfill(2), str(camera)])


def export_group(path_out: str,
                 group_id: str,
                 camera: int = 1) -> None:
    bpy.context.scene.camera = bpy.data.objects[f"Camera.Scenario.O{camera}"]
    for shape_id in clean_and_get_shape_ids(group_id):
        export_shape(path_out, shape_id, camera)


def export_shape(path_out: str,
                 shape_id: str,
                 camera: int = 1) -> None:
    shape = bpy.data.objects[shape_id]
    old_location = move(shape_id, [0, 0, 0])
    show_object(shape_id)
    bpy.context.view_layer.objects.active = shape
    for frame in range(1, 32):
        frame_id = f"C{str(frame).zfill(2)}"
        show_object(frame_id)
        for rotation in rotation_vectors():
            rotate_global(shape, rotation)
            bpy.context.scene.render.filepath = os.path.join(
                path_out,
                file_name(shape_id, rotation, frame, camera)
            ) + "."
            bpy.context.scene.render.use_file_extension = False
            bpy.ops.render.render(layer="FreeStyle", write_still=False)
        hide_object(frame_id)
    hide_object(shape_id)  # explicit rotate 0, 0, 0
    move(shape_id, old_location)
