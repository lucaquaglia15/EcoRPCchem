# This folder contains the analysis scripts used

## Folder strucutre

```
|_laserMicroscope
| |_laserPlotter.py
| |_vk4stitcher.py
|
|_PDC
| |_PDCanalysis.py
|
|_vk4reader
| |_vk4reader
| | |_ __init__.py
| | |_correction.py (remove tilt/offset from the raw data)
| | |_plot.py 
| | |_reader.py (load the data)
| | |_vk4extractor.py
| |
| |_setup.py
|
|_trends
| |_drying.py
| |_plotPressure.py
| |_resistivityPlotter.py
| |_vesselCondition.py
|
|_SEM
| |_SEM.py
| |_SEM_elementalMap.py
| |_SEM_multiPlot.py
| |_mergeJSON.py
| |_runSemAnalysis.sh
```
## Folder description

- laserMicroscope: folder which containts the codes used to analyze the laser microscope (VK-X3000) data
    - laserPlotter.py: plot a 2D of .vk4 files from laser microscope
    - vk4stitcher.py: test of code to merge ("stitch") different .vk4 files from laser microscope

- PDC: folder which containts the codes used to analyze the PDC data
    - PDCanalysis.py: simple code to analyzedata coming from the PDC setup

- vk4reader: library implemented using this [code](https://github.com/torkian/vk4-python-driver.git). The data from the microscope is in .vk4 format and this library helps opening up those files. To install the library run the following commands:
    - Download the folder and place it in `~`
    - Execute `python3 -m pip install -e ~/vk4reader --user`
    - Test the installation with `python3 -c "import vk4reader; print(vk4reader.__file__)"` from which you should get something like `~/vk4reader/vk4reader/__init__.py`
    - Once installed, you can load it in your analysis programs (as it is done in the file under `laserMicroscope/basicPlot.py`)

- trends: folder which contains the codes used to plot the trend in time of the different varabiels monitored during exposure
    - drying.py: code to use to plot the weight of bakelite samples during the drying process in the oven to measure water absorption
    - plotPressure.py: code to use to plot the trend of the pressure data within the vessel during the filling process
    - resistivityPlotter.py: code to use to plot the trend of the resistivity measured with the HP4339B high resistance meter for different materials
    - vesselCondition.py: code to use to plot the environmental parameters within the vessel and the lab

- SEM: folder which contains the codes used to run the analysis on the EDX data obtained from the SEM
    - SEM.py: main code to analyze EDX spectra. It filters the data, calculate baseline and removes it, finds peak and itegrate them to have concentrations estimates and saves output to .json files
    - SEM_elementalMap.py: plots the 2D elemental map (when it has been acquired)
    - SEM_multiPlot.py: plots several EDX spectra on the same plot
    - mergeJSON.py: it opens all the .json files from each EDX spot/area obtained from SEM.py and saves all the data from a given area in a global .json file
    - runSemAnalysis.sh: script used to run multiple times SEM.py on different files and enabling saving of the plots       