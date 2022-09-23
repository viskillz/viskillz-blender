import os

import bpy
from viskillz.blender.common import move, rotate_global, scale_object
from viskillz.blender.constants import rotation_vectors, COLLECTION_PERMUTATIONS
from viskillz.blender.scene import delete_collection, show_object, hide_object
from viskillz.blender.stages.common import clean_and_get_shape_ids


def export_group(path_out: str,
                 group_id: str) -> None:
    for original_id in clean_and_get_shape_ids(group_id):
        scaled_shape_ids = scale_object(bpy.data.objects[original_id])
        for shape_id in scaled_shape_ids:
            export_shape(path_out, shape_id)
        delete_collection(COLLECTION_PERMUTATIONS)


def export_shape(path_out: str,
                 shape_id: str) -> None:
    def inner_file_name(shape_id: str, rotation, frame: int):
        return ".".join([shape_id, "".join([str(r // 90) for r in rotation]), str(frame).zfill(2)])

    shape = bpy.data.objects[shape_id]
    old_location = move(shape_id, [0, 0, 0])
    show_object(shape_id)
    bpy.context.view_layer.objects.active = shape

    rotations = rotation_vectors()
    for frame in range(1, 32):
        frame_id = f"R{str(frame).zfill(2)}"
        show_object(frame_id)
        for rotation in rotations:
            rotate_global(shape, rotation)
            out_file = os.path.join(path_out, inner_file_name(shape_id, rotation, frame))
            bpy.ops.export_scene.gltf(filepath=out_file, use_selection=True)
        hide_object(frame_id)
    hide_object(shape_id)  # explicit rotate 0, 0, 0
    move(shape_id, old_location)
