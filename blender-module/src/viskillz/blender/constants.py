from typing import List, Tuple

COLLECTION_FRAMES_2D = "Frames.2D"
COLLECTION_FRAMES_3D = "Frames.3D"
COLLECTION_PERMUTATIONS = "Permutations"
COLLECTION_SHAPES = "Shapes"
COLLECTION_TMP = "Tmp"

HEADING_PERMUTE_SHAPE = "\t".join([f"{'time':<9}", f"{'shape':<16}", f"{'cor':>3}", f"{'emp':>3}"])


def rotation_vectors(generate_all: bool = False) -> List[List[int]]:
    """
    Returns the 24 unique rotation vectors.
    :param generate_all: tells whether all the possible rotations should be returned or not
    :return: the list of vectors
    """
    rotations = []
    for i in range(4):
        for j in range(4):
            for k in range(4):
                rotations.append([i * 90, j * 90, k * 90])

    return rotations \
        if generate_all \
        else [rotation for rotation in rotations if rotation[0] == 0 or (rotation[0] == 90 and rotation[1] in [0, 180])]


def plane_vectors(scale: float = 2.0) -> List[List[Tuple[float, float, float]]]:
    """
    Returns the vectors that describe the intersection planes.
    :param scale: the scaling factor
    :return: the list of vectors
    """
    return [
        [(0, 0, 0), (0, 0, 1), (0, 0, 0)],  # 01
        [(0, 0, -0.8 * scale), (0, 0, 1), (0, 0, 0)],  # 02
        [(0.0, 0.0, 0.8 * scale), (0, 0, 1), (0, 0, 0)],  # 03
        [(0, 0, 0), (0, 1, 0), (90, 0, 0)],  # 04
        [(0, 0.8 * scale, 0), (0, 1, 0), (90, 0, 0)],  # 05
        [(0, -0.8 * scale, 0), (0, 1, 0), (90, 0, 0)],  # 06
        [(0, 0, 0), (1, 0, 0), (0, 90, 0)],  # 07
        [[-0.8 * scale, 0, 0], (1, 0, 0), (0, 90, 0)],  # 08
        [(0.8 * scale, 0, 0), (1, 0, 0), (0, 90, 0)],  # 09
        [(0, 0, 0), (0, 1, -1), (-45, 0, 0)],  # ,  # 10
        [(0, 0, 0), (-1, 0, -1), (0, -45, 0)],  # 11
        [(0, 0, 0), (0, -1, -1), (45, 0, 0)],  # 12
        [(0, 0, 0), (1, 0, -1), (0, 45, 0)],  # 13
        [(0, 0, 0), (1, 1, 0), (90, 0, 45)],  # 14
        [(0, 0, 0), (1, -1, 0), (0, 90, 45)],  # 15
        [(0, 0, 0), (-0.5, 0.5, 1), (0, 35.27, 45)],  # 16
        [(0, 0, 0), (-0.5, -0.5, 1), (0, 35.27, -45)],  # 17
        [(0, 0, 0), (0.5, -0.5, 1), (0, -35.27, 45)],  # 18
        [(0, 0, 0), (0.5, 0.5, 1), (0, -35.27, -45)],  # 19
        [(0, scale, 0), (0, 1, -1), (-45, 0, 0)],  # 20
        [(0, -scale, 0), (0, 1, -1), (-45, 0, 0)],  # 21
        [(0, 0, scale), (-1, 0, -1), (0, -45, 0)],  # 22
        [(0, 0, -scale), (-1, 0, -1), (0, -45, 0)],  # 23
        [(0, scale, 0), (0, -1, -1), (45, 0, 0)],  # 24
        [(0, -scale, 0), (0, -1, -1), (45, 0, 0)],  # 25
        [(0, 0, scale), (1, 0, -1), (0, 45, 0)],  # 26
        [(0, 0, -scale), (1, 0, -1), (0, 45, 0)],  # 27
        [(0, scale, 0), (1, 1, 0), (90, 0, 45)],  # 28
        [(0, -scale, 0), (1, 1, 0), (90, 0, 45)],  # 29
        [(0, scale, 0), (1, -1, 0), (0, 90, 45)],  # 30
        [(0, -scale, 0), (1, -1, 0), (0, 90, 45)]  # 31
    ]
