#!/usr/bin/env python

# PURPOSE
# This script processes LANDSAT 7 ETM+ images
# 1 - unzip *.gz files
# 2 - import files in GRASS GIS Location of your choice (r.in.gdal)
# 3 - Grouping of Imagery (i.group)
# 4 - Clustering of selected bands (i.cluster)
# 5 - Unsupervised classification (i.maxlik)

# USER HAS TO SET THOSE
# QUIET REPORTS
QIET = True
# OVERWRITE EXISTING FILES
OVR = False
# Setup the path to the Landsat 7 Directories
rsdatapath = os.path.join(os.path.expanduser("~"), "rawData/L7Dir/")
# set L7 Metadata wildcards
wldc_mtl = "*_MTL.txt"

import glob
import os
import subprocess
import sys
import time

# path to the GRASS GIS launch script
# MS Windows
# grass7bin_win = r'C:\OSGeo4W\bin\grass72svn.bat'
# uncomment when using standalone WinGRASS installer
# grass7bin_win = r'C:\Program Files (x86)\GRASS GIS 7.2.0\grass72.bat'
# Linux
grass7bin_lin = 'grass72'

# DATA
# define GRASS DATABASE
# add your path to grassdata (GRASS GIS database) directory
gisdb = os.path.join(os.path.expanduser("~"), "rawData")
# the following path is the default path on MS Windows
# gisdb = os.path.join(os.path.expanduser("~"), "Documents/grassdata")

# specify (existing) location and mapset
location = "L7_Kenya"
mapset = "hempire"

# SOFTWARE
if sys.platform.startswith('linux'):
    # we assume that the GRASS GIS start script is available and in the PATH
    # query GRASS 7 itself for its GISBASE
    grass7bin = grass7bin_lin
else:
    raise OSError('Platform not configured.')

# query GRASS 7 itself for its GISBASE
startcmd = [grass7bin, '--config', 'path']

p = subprocess.Popen(startcmd, shell=False,
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out, err = p.communicate()
if p.returncode != 0:
    print >> sys.stderr, "ERROR: Cannot find GRASS GIS 7 start script (%s)" % startcmd
    sys.exit(-1)
gisbase = out.strip('\n\r')

# Setting GISBASE environment variable
os.environ['GISBASE'] = gisbase
# below is not required with trunk version
os.environ['PATH'] += os.pathsep + os.path.join(gisbase, 'extrabin')
# include path to GRASS addons
home = os.path.expanduser("~")
os.environ['PATH'] += os.pathsep + os.path.join(home, '.grass7', 'addons', 'scripts')
# define GRASS-Python environment
gpydir = os.path.join(gisbase, "etc", "python")
sys.path.append(gpydir)
# Set GISDBASE environment variable
os.environ['GISDBASE'] = gisdb
# import GRASS Python bindings (see also pygrass)
import grass.script.setup as gsetup
import grass.script as grass

gsetup.init(gisbase, gisdb, location, mapset)
from grass.pygrass.modules.shortcuts import raster as r

# Function to get a list of L7 Directories in the rsdatapath
def fn(path):
    for top, dirs, files in os.walk(path):
        return [os.path.join(top, dir) for dir in dirs]

# Find the central location of the Landsat file from metadata
metadata = []
fileList = []
L7Dirs = fn(rsdatapath)
for L7Dir in L7Dirs:
    # Ungzip all of your Landsat7 images in all your directories
    print "Ungzip Landsat files in\t",L7Dir
    #   p=os.system("gzip -d -q "+L7Dir+"/*.gz")
    # Using pthreads on multi-core machines
    #   p=os.system("pigz -d "+L7Dir+"/*.gz")
    # Wait ten seconds for gzip to create the tif images
    # time.sleep(10)

print "Import in GRASS GIS"
for L7f in glob.glob(os.path.join(L7Dir, "*.[tT][iI][fF]")):
        f1 = L7f.replace(L7Dir + "/", "")
        f2 = f1.replace(".TIF", "")
        f3 = f2.replace("_B10", ".1")
        f4 = f3.replace("_B20", ".2")
        f5 = f4.replace("_B30", ".3")
        f6 = f5.replace("_B40", ".4")
        f7 = f6.replace("_B50", ".5")
        f8 = f7.replace("_B61", ".61")
        f9 = f8.replace("_B62", ".62")
        f10 = f9.replace("_B70", ".7")
        f11 = f10.replace("_B80", ".8")
        f12 = f11.replace("L72", "L71")
        L7r = f12.replace("_VCID_", "")
        print "\t> ", L7r
        r.in_gdal(input=L7f, output=L7r, flags="o", overwrite=True)
        fileList.append(L7r)

# creating a color composite by combining three bands in RGB
r.composite(blue="LE07_L1TP_165061_20170113_20170215_01_T1_B2", green="LE07_L1TP_165061_20170113_20170215_01_T1_B3",
            red="LE07_L1TP_165061_20170113_20170215_01_T1_B4", output="LE07_L1TP_165061_composite", overwrite=True)

# Pansharpening of landsat image to 15m resolution
# i.pansharpen with IHS algorithm
# grass.run_command("i.pansharpen", blue="LE07_L1TP_165061_20170113_20170215_01_T1_B2",
#                   green="LE07_L1TP_165061_20170113_20170215_01_T1_B3",
#                   red="LE07_L1TP_165061_20170113_20170215_01_T1_B4",
#                   pan="LE07_L1TP_165061_20170113_20170215_01_T1_B8",
#                   output="ihs432", method="ihs", overwrite=True)


# Grouping raster layers into a group and subgroup as required in clustering and classification
grass.run_command("i.group", group="coastgrp", subgroup="mysubgrp", input="*")
# generating spectral signatures to be used in maximum likelihood classification

grass.run_command("i.cluster", group="coastgrp", subgroup="mysubgrp", signaturefile="sig_cluster_lsat2017", classes="19")
# performing unspervised image classification employing maximum likelihood algorithm
grass.run_command("i.maxlik", group="coastgrp", subgroup="mysubgrp", signaturefile="sig_cluster_lsat2017",
                  output="unsupervised_result")
# Listing the imported raster files
grass.run_command("g.list", flags="f", type="rast")

# grass.run_command("d.mon", start="wx0")
# grass.run_command("d.rast", map="unsupervised_result")
