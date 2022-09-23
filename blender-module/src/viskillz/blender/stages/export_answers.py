import json
import os
from datetime import datetime

import bpy
from viskillz.blender.common import contour_edges, scale_object, create_answer, get_case_id
from viskillz.blender.constants import *
from viskillz.blender.scene import delete_collection, hide_collection, delete_object
from viskillz.common.file import init_dir


def export_group(path: str,
                 group_id: str) -> None:
    shape_ids = []
    for collection in bpy.data.collections[COLLECTION_SHAPES].children:
        if collection.name.startswith(group_id):
            for obj in collection.objects:
                shape_ids.append(obj.name)

    shape_ids.sort()
    for shape_id in shape_ids:
        export_shape(path, shape_id)


def export_shape(path_root: str,
                 original_name: str) -> None:
    delete_collection(COLLECTION_TMP)
    [hide_collection(collection_name) for collection_name in
     [COLLECTION_SHAPES, COLLECTION_FRAMES_2D, COLLECTION_FRAMES_3D, COLLECTION_TMP]]

    planes = plane_vectors(scale=20)
    rotations = rotation_vectors()

    scaleds = scale_object(bpy.data.objects[original_name])

    print(HEADING_PERMUTE_SHAPE)
    for shape_name in scaleds:
        log_buffer = [datetime.now().strftime("%H:%M:%S"), shape_name]
        empty_count = 0
        correct_count = 0

        init_dir(path_root, False)
        json_buffer = dict()
        for rotation in rotations:
            for index in [1, 2, 10, 16, 20]:
                frame_name = "F{:02d}".format(index)
                case_id = get_case_id(frame_name, rotation)
                try:
                    intersection = create_answer(shape_name, planes[index - 1][0], planes[index - 1][1],
                                                 rotation, diff=planes[index - 1][2], ratio_value=20.0)
                    correct_count += 1
                except ValueError:
                    empty_count += 1
                    delete_collection(COLLECTION_TMP)
                    json_buffer[case_id] = "empty"
                    continue

                edges = contour_edges(intersection)
                json_buffer[case_id] = edges
                delete_object(intersection.name)
                delete_collection(COLLECTION_TMP)
        delete_object(shape_name)
        with open(os.path.join(path_root, f"{shape_name}.json"), "w") as file:
            json.dump(json_buffer, file)
            log_buffer += [str(correct_count), str(empty_count)]
            print("\t".join(log_buffer))

    delete_collection(COLLECTION_PERMUTATIONS)
