import math
from typing import List, Tuple, Sequence, cast

import bmesh
import bpy
import mathutils
from mathutils import Matrix
from viskillz.blender.constants import COLLECTION_PERMUTATIONS
from viskillz.blender.scene import hide_object, show_object, delete_object, duplicate_object


def contour_edges(obj: bpy.types.Object) -> List[Tuple[Tuple[float, float], Tuple[float, float]]]:
    """
    Selects the edges that belong to the contour of the object.
    :param obj: the object
    :return: the list of edges
    """
    try:
        bpy.ops.object.mode_set(mode="OBJECT")
    except RuntimeError:
        pass

    hide_object(obj.name)
    bpy.ops.object.select_all(action='DESELECT')
    show_object(obj.name)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    delete_noise_vertices(obj)
    select_faces(obj)
    bpy.ops.mesh.quads_convert_to_tris(quad_method="BEAUTY", ngon_method="BEAUTY")
    bm = bmesh.from_edit_mesh(obj.data)
    edges = []
    for edge in bm.edges:
        if len(edge.link_faces) == 1:
            verts = [obj.matrix_world @ vert.co for vert in edge.verts]
            edges.append(((verts[0].x, verts[0].y), (verts[1].x, verts[1].y)))

    bmesh.update_edit_mesh(obj.data)
    bm.free()
    bpy.ops.object.mode_set(mode="OBJECT")

    return edges


def scale_object(obj: bpy.types.Object,
                 factor: float = 0.7) -> List[str]:
    """
    Creates the scaled permutations of the given object.
    :param obj: the object
    :param factor: the scaling factor
    :return: IDs of the scaled objects
    """

    o = 1
    s = factor

    vectors = [
        [o, o, o], [s, o, o], [o, s, o], [o, o, s],
        [s, s, o], [s, o, s], [o, s, s]
    ]

    names = []
    for vector in vectors:
        scaled_name = duplicate_object(obj.name,
                                       copy_name=obj.name + "." + "".join("1" if c == s else "0" for c in vector),
                                       copy_collection=COLLECTION_PERMUTATIONS)
        scaled = bpy.data.objects[scaled_name]
        scale_object_vec(scaled, vector)
        names.append(scaled_name)
        hide_object(scaled_name)
    return names


def create_answer(shape_name: str,
                  original_co,
                  original_no,
                  rotation,
                  diff: Tuple[float, float, float] = (0, 0, 0),
                  ratio_value: float = 2.0):
    try:
        bpy.ops.object.mode_set(mode="OBJECT")
    except RuntimeError:
        pass

    if "foo" in bpy.data.objects is not None:
        delete_object("foo")

    intersection_name = duplicate_object(shape_name, copy_name="foo")
    bpy.ops.object.select_all(action='DESELECT')
    intersection = bpy.data.objects[intersection_name]
    show_object(intersection_name)
    intersection.select_set(True)
    bpy.context.view_layer.objects.active = intersection

    clear_freestyle_edges(intersection)

    #####
    init_object(intersection, rotation)
    bpy.context.view_layer.update()
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    intersection.scale = (ratio_value, ratio_value, ratio_value)
    co = intersection.matrix_world.inverted() @ mathutils.Vector(original_co)
    no = intersection.matrix_world.inverted() @ mathutils.Vector(original_no)
    co = (co[0], co[1], co[2])
    no = (no[0], no[1], no[2])

    bisect_object(co, no)

    delete_unselected_vertices(intersection)
    delete_noise(intersection)

    bpy.ops.mesh.mark_freestyle_edge(clear=False)
    rotate_global(intersection, diff, clear=True)
    bpy.ops.object.origin_clear()
    bpy.ops.object.origin_set(type="GEOMETRY_ORIGIN", center="MEDIAN")
    bpy.ops.object.mode_set(mode="OBJECT")
    move_to_camera(intersection)
    ratio = get_ratio_global(intersection, value=ratio_value)
    scale_to_camera_global(intersection, ratio)
    bpy.ops.object.mode_set(mode="EDIT")
    return intersection


def get_case_id(frame_name: str,
                rotation: List[float]) -> str:
    return frame_name[1:] + "." + str(rotation[0] // 90) + str(rotation[1] // 90) + str(rotation[2] // 90)


def scale_object_vec(obj, ratio):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for vert in bm.verts:
        vert.co.x *= ratio[0]
        vert.co.y *= ratio[1]
        vert.co.z *= ratio[2]
    bm.to_mesh(obj.data)


def scale_to_camera_global(obj, ratio):
    bm = bmesh.new()
    bm.from_mesh(obj.data)

    global_co = [obj.matrix_world @ vert.co for vert in bm.verts]
    i = 0
    for vert in bm.verts:
        global_co[i].x *= ratio
        global_co[i].y *= ratio
        vert.co = obj.matrix_world.inverted() @ global_co[i]
        i += 1

    bm.to_mesh(obj.data)
    bm.free()


def move(name: str,
         location):
    """
    Moves an object by its name to the given location.
    :param name: the name of the object
    :param location: the new location
    :return: the original location
    """
    shape = bpy.data.objects[name]
    old_location = shape.location.copy()
    shape.location = location.copy()
    return old_location


def move_to_camera(obj: bpy.types.Object,
                   ratio: float = 2.0) -> None:
    """
    Moves an object to the given position, then applies scale on it.
    :param obj: the object
    :param ratio: the scale ratio
    :return:  nothing
    """
    bm = bmesh.new()
    bm.from_mesh(obj.data)

    global_co = [obj.matrix_world @ vert.co for vert in bm.verts]
    co_x = [co.x for co in global_co]
    co_y = [co.y for co in global_co]
    mid_x = (min(co_x) + max(co_x)) / ratio
    mid_y = (min(co_y) + max(co_y)) / ratio

    i = 0
    for vert in bm.verts:
        global_co[i].x -= mid_x
        global_co[i].y -= mid_y
        global_co[i].z = 0
        vert.co = obj.matrix_world.inverted() @ global_co[i]
        i += 1

    bm.to_mesh(obj.data)
    bm.free()


def delete_noise(obj: bpy.types.Object) -> None:
    """
    Deletes all the vertices and edges of an object that can be considered as noise.
    :param obj: the object
    :return: nothing
    """
    delete_noise_vertices(obj)
    delete_noise_edges(obj)


def delete_noise_vertices(obj: bpy.types.Object) -> None:
    """
    Deletes all the vertices of an object that can be considered as noise.
    :param obj: the object
    :return: nothing
    """
    bm = bmesh.from_edit_mesh(obj.data)

    verts = []
    for vert in bm.verts:
        if len(vert.link_edges) == 0:
            verts.append(vert)

    bmesh.ops.delete(bm, geom=verts, context="VERTS")
    bmesh.update_edit_mesh(obj.data)


def delete_noise_edges(obj: bpy.types.Object) -> None:
    """
    Deletes all the edges of an object that can be considered as noise.
    :param obj: the object
    :return: nothing
    """
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="DESELECT")
    bm = bmesh.from_edit_mesh(obj.data)

    faces_select = set()
    for edge in bm.edges:
        count = len(edge.link_faces)
        if count == 1:
            edge.select_set(True)
        elif count == 2 and same_faces(edge.link_faces[0], edge.link_faces[1]):
            faces_select.add(edge.link_faces[1])
            edge.select_set(True)

    bmesh.ops.delete(bm, geom=list(faces_select), context="FACES_ONLY")

    bmesh.update_edit_mesh(obj.data)


def clear_freestyle_edges(obj: bpy.types.Object) -> None:
    """
    Clears all the FreeStyle edges of the object.
    :param obj: the object
    :return: nothing
    """
    bpy.ops.object.mode_set(mode="EDIT")
    select_all_edges(obj)
    bpy.ops.mesh.mark_freestyle_edge(clear=True)


def rotate_global(obj: bpy.types.Object,
                  rotation: Sequence[float],
                  clear: bool = True) -> None:
    """
    Applies an Euler rotation on the object with ZYX order.
    :param obj: the object
    :param rotation: the rotation vector
    :param clear: tells whether the rotation should be based on the initial orientation of the object or not
    :return: nothing
    """

    try:
        bpy.ops.object.mode_set(mode="OBJECT")
    except:
        pass

    if clear:
        obj.rotation_euler = [0, 0, 0]

    rot_z = Matrix.Rotation(math.radians(rotation[2]), 3, "Z")
    rot_y = Matrix.Rotation(math.radians(rotation[1]), 3, "Y")
    rot_x = Matrix.Rotation(math.radians(rotation[0]), 3, "X")
    obj.rotation_euler = (rot_z @ obj.rotation_euler.to_matrix()).to_euler()
    obj.rotation_euler = (rot_y @ obj.rotation_euler.to_matrix()).to_euler()
    obj.rotation_euler = (rot_x @ obj.rotation_euler.to_matrix()).to_euler()


def same_faces(face1: bmesh.types.BMFace,
               face2: bmesh.types.BMFace) -> bool:
    """
    Determines whether two faces can be considered as the same based on their coordinates.
    :param face1: the first face
    :param face2: the second face
    :return: the result
    """
    vertices2 = [v for v in face2.verts if v not in face1.verts]
    return len(vertices2) == 0


def delete_unselected_vertices(obj: bpy.types.Object) -> None:
    """
    Deletes all unselected vertices of the given object.
    :param obj: the object
    :return: nothing
    """
    bpy.ops.object.mode_set(mode="EDIT")
    bm = bmesh.from_edit_mesh(obj.data)

    vertices = []
    for vert in bm.verts:
        if not vert.select:
            vertices.append(vert)

    bmesh.ops.delete(bm, geom=vertices, context="VERTS")
    bpy.ops.mesh.select_all(action="DESELECT")
    for edge in bm.edges:
        edge.select_set(True)

    bmesh.update_edit_mesh(obj.data)


def select_all_edges(obj: bpy.types.Object) -> None:
    """
    Select all edges of the given object.
    :param obj: the object
    :return: nothing
    """
    bpy.ops.object.mode_set(mode="EDIT")
    bm = bmesh.from_edit_mesh(obj.data)
    bpy.ops.mesh.select_all(action="DESELECT")
    for edge in bm.edges:
        edge.select_set(True)

    bmesh.update_edit_mesh(obj.data)


def get_ratio_global(obj: bpy.types.Object,
                     value: float = 2.0) -> float:
    """
    Calculates the ratio which can be used in the further scale operations.
    :param obj: the object
    :param value: the base
    :return: the ratio
    """
    bm = bmesh.new()
    bm.from_mesh(obj.data)

    global_co = [obj.matrix_world @ vert.co for vert in bm.verts]
    co_x = [co.x for co in global_co]
    co_y = [co.y for co in global_co]

    ratio = value / max(max(co_x) - min(co_x), max(co_y) - min(co_y))
    bm.to_mesh(obj.data)
    bm.free()
    return ratio


def bisect_object(co: Tuple[float, float, float],
                  no: Tuple[float, float, float]) -> None:
    """
    Bisects an object with the given plane.
    :param co: the pivot coordinate
    :param no: the normal vector
    :return: nothing
    """
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")

    bpy.ops.mesh.bisect(
        plane_co=cast(List[float], co), plane_no=cast(List[float], no), use_fill=True,
        clear_inner=True, clear_outer=True, threshold=0.0001,
        xstart=0, xend=0, ystart=0, yend=0,
        cursor=1002)


def init_object(obj: bpy.types.Object,
                rotation: List[float]) -> None:
    """
    Initializes the given object using the given rotation vector.
    :param obj: the object
    :param rotation: the rotation vector
    :return: nothing
    """
    bpy.ops.object.mode_set(mode="OBJECT")
    rotate_global(obj, rotation)
    obj.location = (0, 0, 0)
    obj.select_set(True)


def select_faces(obj: bpy.types.Object) -> None:
    """
    Selects and triangulates the faces of the given object.
    :param obj: the object
    :return: nothing
    """
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="DESELECT")
    bm = bmesh.from_edit_mesh(obj.data)
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="BEAUTY", ngon_method="BEAUTY")
