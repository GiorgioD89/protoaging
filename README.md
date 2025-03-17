# protoaging
This folder contains various codes to process experimental clinical data (torques, electromyography data, segmentations):
- Dynamometry_data_elaboration
  - expdata_processing.m
  > to filter the torques recorded by a dynamometer and get the maximum value
- EMG_data_elaboration
  - boh.m
  > to band-pass filter, rectify and low-pass filter EMG traces
- Image_data_elaboration
  - getMuscleVolsCSA.py
  > to extract the volume and maximal cross-sectional area of one or multiple STL files and save them in a CSV file

All scripts are written for MATLAB (v2023b) or Python (v3.8.8)
## Additional dependencies and libraries
The Python scripts to extract muscle volumes and cross-sectional areas requires the following libraries to be installed:
1. numpy
2. pandas
3. vedo[^1]
4. stl
5. vtk
> [!CAUTION]
> The code was tested and worked with *vedo v2022.1.0* and *vtk v9.0.1*.

## Processing C3D files (Gait lab)
Consider using the MOtoNMS[^2] toolbox.

[^1]: M. Musy et al., "vedo, a python module for scientific analysis and visualization of 3D objects and point clouds", Zenodo, 10.5281/zenodo.2561401
[^2]: Mantoan et al. Source Code for Biology and Medicine (2015) 10:12. DOI 10.1186/s13029-015-0044-4. http://www.scfbm.org/content/10/1/12
