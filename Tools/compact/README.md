# Compact revision build tools

The checked native release files are in PCB, CAD and Production. These scripts retain the construction method; they do not replace the need for native KiCad checks.

## PCB

`build_compact.py` uses the archived original native footprints, symbol paths and pad nets, repositions them at full scale, and routes the new 95 mm board. It writes a candidate under `Revisions/Compact_95/PCB`. The final published candidate was opened by KiCad 10.0.7, its zones refilled, and ERC/DRC plus schematic parity checked before Gerber export. Do not send an unchecked generator output directly to fabrication.

## Mechanical rebuild

Python packages used: numpy, scipy, scikit-image, trimesh, manifold3d, vtk, cadquery and its OpenCascade bindings. Installed versions from the validation environment are recorded in CAD/Checks/Software_Versions.json.

From the repository root:

```sh
python Tools/compact/prepare_build.py
python Tools/compact/voxel_ornament.py
python Tools/compact/build_mechanical.py
python Tools/compact/export_assembly_final.py
```

Outputs go to `Build/Compact`, not on top of the published files. The first script copies the exact committed indexed original-source reference and native PCB substrate. The sculpture is remeshed before exact mounts are added. The STEP writer consolidates only coplanar triangles, preserves their boundary loops, and produces a genuine faceted BREP in millimeters. It then reimports the full model and checks every solid.

`mesh_cleanup.py` deals only with degenerate topology and records any operations. The final successful body required zero such operations. No failed experimental decimator or broad automatic mesh repair is part of this published recipe.

The analytic mounts, fitted reference electronics and screw models are a new AI-assisted mechanical revision. They are not the owner's original Tinkercad feature history. The original file is preserved separately.
