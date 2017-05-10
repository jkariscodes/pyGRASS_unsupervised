# PyGRASS unsupervised classification
This script performs unsupervised classification of Landsat7 satellite imagery leveraging on python-GRASS API. Unsupervised image classification is machine-driven and in this GRASS software does the job with some pre-defined parameters. 
# steps
1. First, download a Landsat 7 imagery from http://glovis.usgs.gov/next/ or https://earthexplorer.usgs.gov/ with which you must first log in to be able to download.
2. Extract the archive into /home/username/grassdata/L7Dir/ (Linux) or C://Users/username/grassdata/L7Dir/ (Windows)
3. Download and install GRASS software from https://grass.osgeo.org/download/ 
4. Run GRASS software and define grass LOCATION and MAPSET, these two parameters shall be redefined manually in the script in the following step.
5. Change the rsdatapath value in line #17 to match where Landsat bands have been extracted to. And also change the gisdb value in line #38 from "rawData" to "grassdata", and finally changing the values of Mapset and Location to the names you used to define grass location and mapset.

Executing the script imports data into grass, creates a color infrared (CIR) composite, groups the bands for classification, performs clustering and finally classifies imagery using the maximum likelihood classification algorithm.  

