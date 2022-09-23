import bpy
from viskillz.blender.constants import COLLECTION_TMP, COLLECTION_SHAPES, COLLECTION_FRAMES_2D, COLLECTION_FRAMES_3D
from viskillz.blender.scene import delete_collection, hide_collection


def clean_and_get_shape_ids(group_id: str) -> list[str]:
    delete_collection(COLLECTION_TMP)
    [hide_collection(collection_name) for collection_name in
     [COLLECTION_SHAPES, COLLECTION_FRAMES_2D, COLLECTION_FRAMES_3D, COLLECTION_TMP]]

    shape_ids = []
    for collection in bpy.data.collections[COLLECTION_SHAPES].children:
        if collection.name.startswith(group_id):
            for obj in collection.objects:
                shape_ids.append(obj.name)

    shape_ids.sort()
    return shape_ids
