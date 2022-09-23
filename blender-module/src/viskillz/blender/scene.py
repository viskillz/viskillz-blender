import bpy
from viskillz.blender.constants import COLLECTION_TMP


def toggle_collection(name: str,
                      value: bool) -> None:
    """
    Toggles the visibility of a collection recursively.
    :param name: the name of the collection
    :param value: determines whether the collection should be seen or not
    :return: nothing
    """
    collection = bpy.data.collections[name]
    for obj in collection.objects:
        toggle_object(obj.name, value)
    for child in collection.children:
        toggle_collection(child.name, value)


def toggle_object(name: str,
                  value: bool) -> None:
    """
    Toggles the visibility of an object.
    :param name: the name of the object
    :param value: determines whether the object should be seen or not
    :return: nothing
    """
    try:
        ob = bpy.data.objects[name]
        ob.hide_set(not value)
        ob.hide_render = not value
        ob.hide_viewport = not value
        ob.select_set(value)
    except RuntimeError:
        pass


def delete_collection(name: str) -> None:
    """
    Deletes the objects of a collection by its name.
    :param name: the name
    :return: nothing
    """
    collection = bpy.data.collections[name]
    for obj in collection.objects:
        delete_object(obj.name)


def hide_collection(name: str) -> None:
    """
    Hides the collection by its name.
    :param name: the name
    :return: nothing
    """
    toggle_collection(name, False)


def hide_object(name: str) -> None:
    """
    Hides an object by its name.
    :param name: the name
    :return: nothing
    """
    try:
        toggle_object(name, False)
    except RuntimeError:
        pass


def show_object(name: str) -> None:
    """
    Shows an object by its name.
    :param name: the name
    :return: nothing
    """
    toggle_object(name, True)


def delete_object(name: str) -> None:
    """
    Deletes an object by its name.
    :param name: the name
    :return: nothing
    """
    obj = bpy.data.objects[name]
    bpy.data.objects.remove(obj, do_unlink=True)


def duplicate_object(name: str,
                     copy_collection: str = None,
                     copy_name: str = None) -> str:
    """
    Duplicates an object. It is possible to assign the given name to the new object, then link it to the given collection.
    Without specifying these values, the object will get its default name, and assigned to the TMP collection.

    :param name: the name of the object
    :param copy_collection: the name of the collection to which the new object should be linked
    :param copy_name: the name of the new object
    :return: the name of the new object
    """

    original_intersection = bpy.data.objects[name]
    intersection = original_intersection.copy()
    intersection.data = original_intersection.data.copy()
    bpy.data.collections[COLLECTION_TMP if copy_collection is None else copy_collection].objects.link(intersection)
    if copy_name is not None:
        intersection.name = copy_name
    bpy.context.collection.objects.link(intersection)
    bpy.context.view_layer.update()
    return intersection.name
