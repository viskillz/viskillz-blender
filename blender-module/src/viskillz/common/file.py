import os


def init_dir(path: str,
             delete: bool = True) -> None:
    """
    Initializes a directory in with the given path.
    :param path: the path of the directory
    :param delete: whether the content of an already existing folder should be deleted or not
    :return: nothing
    """
    try:
        os.mkdir(path)
    except FileExistsError:
        if delete:
            for file in [f for f in os.listdir(path)]:
                os.remove(os.path.join(path, file))
