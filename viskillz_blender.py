import asyncio
import json
import os
import subprocess
import sys
from asyncio import streams
from datetime import datetime
from typing import Any, Callable

from viskillz.common.log import StageLogger
from wakepy import keepawake

from viskillz.common.file import init_dir

OUT = "out"
GROUPS = "groups"
SRC = "src"
TYPE = "type"


async def call_async(command: list[str]) -> None:
    process = await asyncio.create_subprocess_exec(
        *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    async def output_filter(
            input_stream: streams.StreamReader,
            output_stream: Any) -> None:
        while not input_stream.at_eof():
            output = await input_stream.readline()
            if output.startswith(b"info"):
                output_stream.buffer.write(output[5:])
                output_stream.flush()

    await asyncio.gather(
        output_filter(process.stderr, sys.stderr),
        output_filter(process.stdout, sys.stdout),
    )
    await process.wait()


def main() -> None:
    with open(sys.argv[1]) as file:
        conf = json.load(file)
        name_conf = os.path.split(sys.argv[1])[-1].split(".")[0]

    blender_version = conf["blender-version"]
    blender_executable = os.path.join(conf["blender-base"], f"Blender {blender_version}", "blender")
    blender_project = conf["blender-project"]
    path_working = conf["working-directory"]
    path_internal_runner = os.path.join(
        conf["blender-base"], f"Blender {blender_version}", blender_version, "scripts", "modules", "viskillz",
        "blender", "runner.py"
    )

    start_time = datetime.now().strftime("%Y%m%d-%H%M%S")
    global_log = dict()

    command_base = [blender_executable, "--background", blender_project, "--python", path_internal_runner, "--"]

    def run_command(group_ids: list[str], path_out: str, args: Callable, is_async: bool = False) -> dict:
        init_dir(os.path.join(path_working, path_out), delete=False)
        for group_id in group_ids:
            formatted_group_id = f"Classic.{str(group_id).zfill(2)}"
            init_dir(os.path.join(path_working, path_out, formatted_group_id), delete=False)

        logger = StageLogger(lambda x: x, 0)

        for group_id in group_ids:
            formatted_group_id = f"Classic.{str(group_id).zfill(2)}"
            path_output_group = os.path.join(path_working, path_out, formatted_group_id)
            logger.start(formatted_group_id)

            command = command_base + args(**{"path_out": path_output_group, "group_id": formatted_group_id})
            asyncio.run(call_async(command)) if is_async else subprocess.call(command)
        return logger.finish()

    for goal_id in range(len(conf["goals"])):
        goal = conf["goals"][goal_id]
        print(f"#{goal_id} / {len(conf['goals'])}", goal[TYPE])

        formatted_goal_id = f"{str(goal_id).zfill(2)}-{goal[TYPE]}"
        global_log[formatted_goal_id] = run_command(goal[GROUPS], goal[OUT], *{
            "scenarios-3d": [
                lambda **kwargs: [
                    "-3d", kwargs["path_out"], kwargs["group_id"]
                ], True
            ],
            "scenarios-2d": [
                lambda **kwargs: [
                    "-2d", kwargs["path_out"], kwargs["group_id"], str(goal["camera"])
                ], True
            ],
            "intersections": [
                lambda **kwargs: [
                    "-ans", kwargs["path_out"], kwargs["group_id"]
                ], True
            ]
        }[goal[TYPE]])

        with open(os.path.join(path_working, f"log-{name_conf}-{start_time}.json"), "w") as file:
            json.dump(global_log, file, indent=2)


if __name__ == "__main__":
    with keepawake(keep_screen_awake=True):
        main()
