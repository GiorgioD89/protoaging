# protoaging
This folder contains various codes to process experimental clinical data (electromyohgraphy, dynamometry, segmentations):
- Muscle volumes
  - getMuscleVolsCSA.py
- Dynamometry data
  - expdata_processing.m
- Electromyography data
  - boh.m
- Biomechanical simulations in OpenSim[^1][^2]
  - os_batch_processing.m
  - genFoldersTags.m

All scripts are written for MATLAB (v2023b) or Python (v3.8.8)
## Additional dependencies and libraries
The Python scripts to extract muscle volumes and cross-sectional areas requires the following libraries to be installed:
1. numpy
2. pandas
3. vedo[^4]
4. stl
5. vtk
> [!CAUTION]
> The code was tested and worked with *vedo v2022.1.0* and *vtk v9.0.1*.

## Processing C3D files (Gait lab)
Consider using the MOtoNMS[^3] toolbox.

[^1]: Delp et al (2007).
[^2]: Seth et al (2018).
[^3]: Mantoan et al (2015).
[^4]: vedo
