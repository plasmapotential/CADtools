#cad_tester.py
#FYI this only works with python2 on centos7


FREECADPATH = '/usr/lib64/freecad/lib'
import sys
sys.path.append(FREECADPATH)
import FreeCAD
import FreeCADGui as Gui
import Part
import numpy as np

stepfile = '/u/tlooby/NSTX/CAD/2019_07/30deg/simple_cube.step'
shape = Part.Shape()
shape.read(stepfile)

faces = []
COM = []
norms = []
for f in shape.Faces:
    faces.append(f)
    #get center of mass for each face
    COM.append(f.CenterOfMass)
    #Normal at COM
    umin, umax, vmin, vmax = f.ParameterRange
    u = (umax - umin) / 2.0
    v = (vmax - vmin) / 2.0
    norms.append(f.normalAt(u,v))
