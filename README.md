# protoaging
This folder currently contains a Pyhton script to process 3D muscle volumes (STL files):
- Image_data_elaboration
  - getMuscleVolsCSA.py
  > to extract the volume and maximal cross-sectional area of one or multiple STL files and save them in a CSV file

The scipt was written, tested and used in Python v3.8.8

> [!NOTE]
> The *protoaging* folder may be expanded in the future to include additional scripts to process different types of experimental data (torques, electromyography data)

## Additional dependencies and libraries
The Python script to extract muscle volumes and cross-sectional areas requires the following libraries to be installed:
1. numpy
2. pandas
3. vedo[^1]
4. stl
5. vtk
> [!CAUTION]
> The code was tested and worked with *vedo v2022.1.0* and *vtk v9.0.1*.

[^1]: M. Musy et al., "vedo, a python module for scientific analysis and visualization of 3D objects and point clouds", Zenodo, 10.5281/zenodo.2561401
