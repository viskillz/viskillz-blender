import sys

import viskillz.blender.stages.export_answers as permute
from viskillz.blender.stages import export_svg, export_glb


def run() -> None:
    args = sys.argv[sys.argv.index("--") + 1:]
    if args[0] == "-ans":
        permute.export_group(path=args[1], group_id=args[2])
    elif args[0] == "-3d":
        export_glb.export_group(path_out=args[1], group_id=args[2])
    elif args[0] == "-2d":
        export_svg.export_group(path_out=args[1], group_id=args[2], camera=int(args[3]))


if __name__ == "__main__":
    run()
