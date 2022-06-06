#creates a plane with 1 edge defined as a polynomial
#Engineer: T Looby
#date: 20220606

import numpy as np
import sys
import os

# daily build binary freecad path
FreeCADPath = '/usr/lib/freecad-daily/lib'
#append FreeCAD to python path
sys.path.append(FreeCADPath)

import FreeCAD
import Part
import Import

outStep= '/home/tom/source/dummyOutput/curve.step'
outStd= '/home/tom/source/dummyOutput/curve.FCStd'

mergePt = np.array([1.84, 1.04])
topPt = np.array([2.03, 0.86])
btmPt = np.array([2.43, 0.0])

cornerPts = np.array([[3.0, 1.04],[3.0, 0.0]])

#coefficient index
idxC = 0

coeffs = [
            [2.43, 0.0, -0.525412, 0.0, -0.0334444, 0.0, 0.0],
            [2.43, 0.0, -0.443139, 0.0, -0.132090,  0.0, 0.0],
            [2.43, 0.0, -0.374472, 0.0, -0.203461,  0.0, 0.0],
            [2.43, 0.0, -0.313361, 0.0, -0.262355,  0.0, 0.0],
            [2.43, 0.0, -0.247534, 0.0, -0.325026,  0.0, 0.0]
        ]

labels = ['V3a', 'V3b', 'V3c', 'V3d','V3e']

zLin = np.linspace(btmPt[1],topPt[1],100)

#plot a figure of the polynomials
#fig = go.Figure()
#for c in coeffs:
#    p = np.polynomial.Polynomial(c, domain=domain, window=window)
#    fig.add_trace(go.Scatter(x=p(z), y=z))
#fig.update_yaxes(scaleanchor = "x",scaleratio = 1,)
#fig.show()

#build polyline part object
doc = FreeCAD.newDocument()

for idx,c in enumerate(coeffs):
    p = np.polynomial.Polynomial(c)
    r = p(zLin)

    #xyz coordinates at phi=0.  convert to mm
    x = r*1e3
    y = np.zeros((len(r)))*1e3
    z = zLin * 1e3

    lines = []
    for i in range(len(z)-1):
        V1 = FreeCAD.Vector(x[i], y[i], z[i])
        V2 = FreeCAD.Vector(x[i+1], y[i+1], z[i+1])
        lines.append(Part.makeLine(V1,V2))

    #add the merge point where we stitch this curve back into RZ contour
    V1 = FreeCAD.Vector(x[-1], y[-1], z[-1])
    V2 = FreeCAD.Vector(mergePt[0]*1e3, 0.0, mergePt[1]*1e3)
    lines.append(Part.makeLine(V1,V2))

    #add the corner points to stitch this into a part
    V1 = FreeCAD.Vector(mergePt[0]*1e3, 0.0, mergePt[1]*1e3)
    V2 = FreeCAD.Vector(cornerPts[0,0]*1e3, 0.0, cornerPts[0,1]*1e3)
    lines.append(Part.makeLine(V1,V2))

    V1 = FreeCAD.Vector(cornerPts[0,0]*1e3, 0.0, cornerPts[0,1]*1e3)
    V2 = FreeCAD.Vector(cornerPts[1,0]*1e3, 0.0, cornerPts[1,1]*1e3)
    lines.append(Part.makeLine(V1,V2))

    V1 = FreeCAD.Vector(cornerPts[1,0]*1e3, 0.0, cornerPts[1,1]*1e3)
    V2 = FreeCAD.Vector(x[0], y[0], z[0])
    lines.append(Part.makeLine(V1,V2))


    shp = Part.Shape(lines)
    w = Part.Wire(lines)
    face = Part.Face(w)

    obj = doc.addObject("Part::Feature", "polynomial_"+labels[idx])
    obj.Shape = face

    doc.recompute()

#doesnt work for faces from wires
#Import.export(obj, outStep)
#save freecad file
doc.saveCopy(outStd)
