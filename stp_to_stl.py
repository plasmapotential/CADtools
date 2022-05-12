#stp_to_stl.py
#Description:   Reads STP file and converts to STL file
#Engineer:      T Looby
#Date:          20191106

FREECADPATH = '/opt/freecad/appImage/squashfs-root/usr/lib'
import sys
sys.path.append(FREECADPATH)
import FreeCAD
import FreeCADGui as Gui
import Part
import numpy as np
import Import
import time
import Mesh
import MeshPart

t0 = time.time()

#infile = '/u/tlooby/NSTX/CAD/tests/IBDH_tile.step'
#outfile = '/u/tlooby/NSTX/CAD/tests/IBDH_tile.stl'

infile = '/u/tlooby/NSTX/CAD/simple_shapes/simple_cube.step'
outfile = '/u/tlooby/NSTX/CAD/simple_shapes/simple_cube.stl'

shape = Part.Shape()
shape.read(infile)
print("CAD STEP read took {:f} seconds".format(time.time() - t0))
mesh_shp = MeshPart.meshFromShape(shape, MaxLength=10.0) #[mm]
#mesh_shp = MeshPart.meshFromShape(shape)
print("Part mesh took {:f} seconds".format(time.time() - t0))
mesh_shp.write(outfile)

print("\nCompleted...")
print("Total execution took {:f} seconds\n\n".format(time.time() - t0))

#Times fro 30deg lwrhalf
#1mm 3590sec
#2mm
#
