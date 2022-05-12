#strip_step_file.py
#Description:   Reads CAD file and strips unnecessary parts
#Engineer:      T Looby
#Date:          20191031 (boo!)

FREECADPATH = '/opt/freecad/appImage/squashfs-root/usr/lib'
import sys
sys.path.append(FREECADPATH)
import FreeCAD
import FreeCADGui as Gui
import Part
import numpy as np
import Import
import time

"""
You can either explicitly define a list of parts, or import a csv file into an
array of strings.  If there are several similar parts that share a common
prefix, you can only include the prefix and the parser will keep all parts that
contain the prefix.
Example:
part_list = ['E-ED1434-011', 'E-ED1434-010']
Prefix only:
part_list = ['E-ED1434']
"""

t0 = time.time()
#File that includes parts or part prefixes, each on their own line
partfile = '/u/tlooby/NSTX/CAD/2019_07/NSTXU_PFC_BOM.csv'
part_list = []
with open(partfile) as f:
    part_list = f.read().splitlines()
print("Read parts list...")

#Input / Output STEP files
infile = '/u/tlooby/NSTX/CAD/2019_07/e-ed1384-02_asm.stp'
#infile = '/u/tlooby/NSTX/CAD/30deg/30deg_lowerhalf.step'
outfile = '/u/tlooby/NSTX/CAD/2019_07/test_parser_output.step'

#If a shape has a label in part_list, keep it
CAD = Import.open(infile)
newobj = []
for i in App.ActiveDocument.Objects:
    if any(substring in i.Label for substring in part_list):
    #if i.Label in part_list:
        newobj.append(i)

#Export to a new step file
Import.export(newobj, outfile)
print("Step file export complete.")
print("Parser execution took {:f} seconds".format(time.time() - t0))
