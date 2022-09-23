# `viskillz-blender`

## About the package

The aim of package `viskillz-blender` is to support instructors, researchers, and students who have to deal with Mental Cutting Test exercises. The package uses the Python API of Blender and performs an automatized permutation on manually designed meshes using intersection planes and applying rotation and scaling operators. The package has three components.

## The environment

To enhance the development of MCT exercises, we have designed an environment that consists of three components:
* A [Blender project](/examples/viskillz.blend) containing the set of our manually designed meshes and permutation planes.
* An [internal package](/blender-module/src/) implementing the automatic permutation using the Python API of Blender. This package should be located in the folder of Blender, making users able to call its functions directly with the use of Blender's built-in interpreter.
* A [wrapper module](/viskillz_blender.py), which offers an opportunity to execute goals with the direct use of Blender's interpreter but invokes the internal runner as subprocess.

The core of package `viskillz-blender` is the Blender-based package and its wrapper module. However, a Blender project is needed with the given structure to use the script since it operates on a pre-defined structure, accessing the existing models and creating temporary ones. Thus, we describe the package's features with examples based on our Blender project, which consists of more than 200 manually designed meshes. On the other hand, it can be used as a reference project, allowing users to use its models and add new ones or derive their own projects with the same structure. 

## Setup

### Install and configure Blender

1. [Download](https://www.blender.org/download/) the latest version of Blender and install it.
2. Enable FreeStyle SVG Exporter in Blender:

    ```
    Properties editor ‣ Render ‣ Freestyle SVG Export
    ```

### Add the package to Blender

To use the Blender package, copy the packages (excluding folder `src`) of the project folder `blender-modules` to the corresponding folder of your Blender installation.

* The default location of the folder is the following:
 
    ```
    c:\Program Files\Blender Foundation\Blender {VERSION}\{VERSION}\scripts\modules\
    ```

* In the case of Blender 3.3, the path of the folder is the following:

    ```
    c:\Program Files\Blender Foundation\Blender 3.3\3.3\scripts\modules\
    ```

### Install a Python interpreter

As Blender's Python interpreter is not designed to install packages and be used for standard processes, a standalone Python interpreter is recommended for the wrapper script.

We recommend two options to download and install a Python interpreter:

* [Download](https://www.python.org/downloads/) and install a Python interpreter directly.
* [Download](https://docs.conda.io/en/latest/miniconda.html) Miniconda and create an environment 

    1. Create an environment with name `mct` (the name can be changed):

        ```
        conda create --name mct python=3.10
        ```
    2. Activate the environment (to access command `pip` in command-line):

        ```
        conda activate mct
        ```
    
    For further commands and configuration, see the official [Conda Cheat Sheet](https://docs.conda.io/projects/conda/en/4.6.0/_downloads/52a95608c49671267e40c689e0bc00ca/conda-cheatsheet.pdf).

### Install package [`viskillz-common`](https://github.com/viskillz/viskillz-common)

The wrapper script uses functions of our package `viskillz-common`. Thus, install this package directly from our GitHub repository, using the following `pip` command:

```
pip install git+https://github.com/viskillz/viskillz-common#egg=viskillz-common
```

### Install package [`wakepy`](https://github.com/np-8/wakepy)

To prevent your computer from falling asleep during the rendering or exporting process, we use package `wakepy` in the wrapper script. Install this package using the following `pip` command:

```
pip install wakepy
```

### The reference environment

Our package was developed and tested in an environment having the following properties:

* Blender version: 3.3
* Conda version: 4.14.0
* Python interpreter version: 3.10.6
* `wakepy` version: 0.5.0
* OS: Windows 11 Home

## The Blender project

Our Blender project file has a special structure, which can be processed automatically by the internal package:

* Collection `Frames.3D` contains the objects representing the cutting planes in 3D assets, having IDS `R01`-`R31`.
* Collection `Frames.2D` contains the objects representing the cutting planes in 2D assets, having IDS `C01`-`C31`.
* Collection `Cameras` contains two cameras:

    | Name                 |                             Example                             |
    | -------------------- | :-------------------------------------------------------------: |
    | `Camera.Scenario.O1` | ![Camera.Scenario.O1](/resources/Classic.0100.000.01.1.0000.svg) | width=100) |
    | `Camera.Scenario.O2` | ![Camera.Scenario.O1](/resources/Classic.0100.000.01.2.0000.svg) | width=100) |

* Collection `Shapes`contains our models, organized in groups. A group of models has the collection `Classic.GG`, and manually designed permutations are entries of them having IDS `Classic.GGMM`. 
* Collections `Tmp` and `Permutations` are empty, and temporary objects are being added and removed dynamically during the execution of the script.

## Goals

With the use of the wrapper module, users can specify their workflow in a JSON document, specifying the following goals:

* `intersections`: Permutes the shapes of the given groups using all the permutation factors. The output of this goal is a JSON document for each involved group that contains the descriptions of intersections represented by their coordinates.
* `scenarios-3d`: Permutes the shapes of the given groups using all the permutation factors. The output of this goal is a set of 2D scenarios encoded in GLB assets.
* `scenarios-2d`: Permutes the shapes of the given groups using all the permutation factors. The output of this goal is a set of SVG scenarios encoded in SVG assets.


## Configuration

The configuration of the execution has five properties:

* `working-directory`: The path of the working directory in which the output folders of the goals should be created.
* `blender-project`: The path of the `.blend` file, which contains the intersection planes and models.
* `blender-version`: The version of the Blender software. This value will be used in the string interpolations accessing the internal interpreter and our package.
* `blender-base`: The path of folder `"Blender Foundation"`, in which the Blender installation(s) can be found.

These properties are followed by array `goals`, which contains the sequence of goals:

* `type`: The type of the goal (`intersections` / `scenarios-2d` / `scenarios-3d`)
* `out`: The subdirectory of directory `working-directory`, in which the output should be written.
* `groups`: An array containing the sequence of group ID-s that should be executed in the given order.
* `camera`: Determines which camera should be used in the goal. Being processed only in the case of goal `scenarios-2d` since the intersections are camera-independent and GLB models can be rotated.

The path of the configuration should be passed as the first (and only) command-line argument to the wrapper module:

```
python d:/mct/viskillz_blender.py d:/mct/configuration.json
```

## Example

### Configuration

```json
{
    "working-directory": "d:\\mct",
    "blender-project": "d:\\mct\\viskillz.blend",
    "blender-version": "3.3",
    "blender-base": "c:\\Program Files\\Blender Foundation",
    "goals": [
        {
            "type": "intersections",
            "out": "out-intersections",
            "groups": [1, 3]
        },
        {
            "type": "scenarios-2d",
            "out": "out-scenarios-2d-1",
            "groups": [1, 3],
            "camera": 1
        },
        {
            "type": "scenarios-2d",
            "out": "out-scenarios-2d-2",
            "groups": [1, 3],
            "camera": 2
        },
        {
            "type": "scenarios-3d",
            "out": "out-scenarios-3d",
            "groups": [1, 3]
        }
    ]
}
```

### Explanation

1. The first goal has the type `intersections`. Thus, it generates the coordinates of the intersections. It will create folder `d:\mct\out-intersections`, and the intersections of each group will be written to a separate folder. The intersections of each scaled mesh will have their JSON document.
2. The second goal has the type `scenarios-2d`. Thus it renders the scenarios in SVG documents.
   1. The script creates folder `d:\mct\out-scenarios-2d-1`.
   2. The script processes groups `1` and `3` (in this order). For each group, it creates a subdirectory and renders the SVG assets. Property `camera` has a value of `1`. Thus `Camera.Scenario.O1` is used.
3. The third goal has the type `scenarios-2d`. Thus it renders the scenarios in SVG documents.
   1. The script creates folder `d:\mct\out-scenarios-2d-2`.
   2. The script processes groups `1` and `3` (in this order). For each group, it creates a subdirectory and renders the SVG assets. Property `camera` has a value of `2`. Thus `Camera.Scenario.O2` is used.
4. The fourth goal has type `scenarios-3d`. Thus it generates and exports the scenarios in GLB documents.
   1. The script creates folder `d:\mct\out-scenarios-3d`.
   2. The script processes groups `1` and `3` (in this order). For each group, it creates a subdirectory and writes the GLB assets.
 
## Remarks

1. The wrapper script can invoke each subprocess using function `subprocess.call()`. However, Blender logs a lot in the case of goals `scenarios-2d` and `scenarios-3d`. Thus, an alternate, `async` execution was designed to filter the standard output and standard error channels. In this case, only lines with the prefix `info` are logged.
2. Blender appends the frame ID automatically to the names of the SVG documents. Thus, each file name ends with `0000.svg` suffix.