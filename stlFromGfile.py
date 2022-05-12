# stlFromGfile.py
# Description:  Makes 3D STL mesh file from gfile rlim,zlim.  also function to create STP from STL
# Engineer:     T Looby
# Date:         20200508
import sys
FREECADPATH = '/opt/freecad/squashfs-root/usr/lib'
EFITPath = '/home/tom/source'
sys.path.append(FREECADPATH)
sys.path.append(EFITPath)
import FreeCAD

import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d
import pandas as pd
from textwrap import dedent
import Part
from stl import mesh
import stl
import EFIT.equilParams_class as EP

def gfile2STL(gfile,
              numS=100, # Resolution in S direction
              minS=29, # Minimum S.  S=0 is midplane [m]
              maxS=32, # S greater than actual s maximum defaults to s[-1] [m] Max=7.77270047363658
              numPhi=2, # Resolution in phi direction
              minPhi=78.75, # Minimum toroidal angle [deg]
              maxPhi=90, # Maximum toroidal angle [deg]
              plotmask=True, # Set to true to plot cross section in 2D plane
              shrinkmask = False, # Shrink rlim,zlim
              interpolateMask = False, # interpolate wall = True, don't interpolate = false
              stlfile=None, # call w/ filename to enable stlfile saving
              ):
    """
    creates gfile from STL

    Also contains function to create STEP from STL

    S is a variable that walks along wall from inner midplane (a wall coordinate).
    minS and maxS can be used to only revolve a section of wa;;
    minS is where along S we start our STL file
    maxS is where along S we stop our STL file
    S starts where rlim,zlim start in gFile
    """
    ep = EP.equilParams(gfile)
    inputdata = pd.DataFrame({'R':ep.g['wall'][:,0], 'Z':ep.g['wall'][:,1]})
    # Invert to follow MAFOT convention, walking 'down' tokamak inner wall first
    #rawdata = rawdata[::-1]
    #rawdata = rawdata[:-1]
    print('Created MHD Object')

    if shrinkmask:
        rawdata = shrinkage(inputdata,1.1)
    else: rawdata = inputdata


    # Call distance function to return distance along S
    dist = distance(rawdata)

    # Constrain maximum S
    if maxS > dist[-1]:
        maxS = dist[-1]
    print(dist[-1])

    if interpolateMask is True:
        # Resolution we need given the inputs
        resolution = (maxS - minS)/float(numS)

        # Calculate how many total grid points we need based upon resolution and
        # total distance around curve/wall
        numpoints = dist[-1]/resolution

        # Spline Interpolation (linear) - Make higher resolution wall.
        interpolator = interp1d(dist, rawdata, kind='slinear', axis=0)
        alpha = np.linspace(0, dist[-1], numpoints)
        interpolated_points = interpolator(alpha)
        newdist = distance(interpolated_points)

    else:
        interpolated_points = rawdata.values
        newdist = dist

    print('Finding Section')

    phis = np.linspace(minPhi, maxPhi, numPhi)
    print("Phi:")
    print(phis)
    #the tesselation below cuts off the last phi step unless we extend the
    #toroidal sweep out an extra step here
    maxPhi = (phis[1] - phis[0]) + maxPhi
    numPhi+=1
    phis = np.linspace(minPhi, maxPhi, numPhi)
    # Now take the piece of curve between minS and maxS and copy in phi
    # idx true when we are between minS and maxS
    idx = (newdist >= minS)*(newdist <= maxS)
    # i is counter for phi direction
    # j is counter for entire curve (S direction)
    # k is counter for section between minS and maxS
    # Initialize data matrix
    testidx=0
    for i in range(len(idx)):
        if idx[i]:
            testidx+=1
    data = np.zeros((testidx*numPhi, 3))
    #Overwrite old numS to match our new numS
    numS = testidx

    # Fill out data matrix
    k=0
    for i in range(len(phis)):
        for j in range(len(idx)):
            if idx[j]:
                #R
                data[k,0] = interpolated_points[j,0]
                #Phi
                data[k,1] = phis[i]
                #Z
                data[k,2] = interpolated_points[j,1]
                k+=1

    print('Filling out matrix')
    # If plotmask is true, show a plot
    if plotmask:
        # Plot machine perimeter with overlaid section of interest
        plt = plot2d_whole(interpolated_points)
        plt = plot2d_piece(data)
        plt.legend(loc='lower right')
        plt.show()

    print('Writing STL')
    # If stlfile is defined, write an stl file from point cloud
    if stlfile is not None:
        writestlfile(data, stlfile, numS, numPhi)

    print("Completed")


def stl2step(stlfile,stpfile, resolution):
    """
    creates stp file from stl
    stlfile is input STL file
    stpfile is output STEP file
    resolution is allowable deviation from surface
    """

    mesh = Mesh.Mesh()
    mesh.read(stlfile)
    mesh.fillupHoles()
    shape = Part.Shape()
    shape.makeShapeFromMesh(mesh.Topology, resolution)
    shape.exportStep(stpfile)


#==============================================================================
#                   Secondary Helper Functions
#==============================================================================

# Calculate distance along curve/wall (also called S):
def distance(rawdata):
    distance = np.cumsum(np.sqrt(np.sum(np.diff(rawdata,axis=0)**2,axis=1)))
    distance = np.insert(distance, 0, 0)
    return distance

# Plot entire curve / machine wall
def plot2d_whole(data):
    plt.scatter(data[:,0], data[:,1], label='B-splined Perimeter')
    return plt

# Plot section of wall between minS and maxS
def plot2d_piece(data):
    plt.scatter(data[:,0], data[:,2], label='Section of Interest', marker='+')
    return plt

# Write a gridfile in R, Phi, Z, coordinates
def writegridfile(data, outfile, numS, numPhi):
    header = """\
                Grid points along the NSTX wall for MAFOT field line tracing.
                Points are about evenly spaced in Swall, the length along the wall, and toroidal angle phi.
                If R,Z == 0 for a grid point, it is outside of the CAD defined wall segment.
                Nswall = {:d}
                Nphi = {:d}
                R [m]\t\t\tphi [deg]\t\t Z [m] """.format(numS, numPhi)
    np.savetxt(outfile, data, delimiter = '\t', header=dedent(header), fmt='%.14f')
    print('Wrote grid file for MAFOT...')

# Convert (R, Phi, Z) to (x, y, z)
def cyl2xyz(data):
    xyzdata = np.zeros((np.shape(data)))
    xyzdata[:,0] = data[:,0]*np.sin(np.deg2rad(data[:,1]))
    xyzdata[:,1] = data[:,0]*np.cos(np.deg2rad(data[:,1]))
    xyzdata[:,2] = data[:,2]
    return xyzdata

# Using fact that these points are ordered along lines of constant phi,
# tesselate surface.
def tesselate(points, numPhi, numS):
    print("Tesselating point cloud.")
    faces = []
    phicounter = 0
    while phicounter < (numPhi-2):
        # May need to change upper bound of loop for discontinuous Surfaces
        # ie: range(numS) or range(numS-1)
        for idx in range(numS-1):
            i = phicounter*numS + idx
            # Lower Triangle
            #face = [i, i+1, i+1+numS]      #flip normals
            face = [i, i+1+numS, i+1]
            faces.append(face)
            # Upper Triangle
            #face = [i,i+1+numS, i+numS ]   #flip normals
            face = [i, i+numS, i+1+numS]
            faces.append(face)

        phicounter += 1
    return np.asarray(faces)

# Take (R, phi, Z) pointcloud, create a 3D surface from it, then save as stl
def writestlfile(data, outfile, numS, numPhi):
    xyzdata = cyl2xyz(data)*1000.0
    faces = tesselate(xyzdata, numPhi, numS)
    wall = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            # invert 1.0 to invert face vecs (inside of tokamak)
            #dir = 1.0
            #dir = -1.0
            wall.vectors[i][j] =  xyzdata[f[j],:]
    wall.save(outfile)
    print('Saved STL file.')


# Shrink radius of wall by specified amount
def shrinkage(data,delta):
    r0 = (np.max(data['R']) - np.min(data['R']))/2.0 + np.min(data['R'])
    z0 = (np.max(data['Z']) + np.min(data['Z']))
    newdata = np.zeros(np.shape(data), type(data.iloc[0,0]))
    for i in range(len(data)):
        newdata[i,0] = (data['R'][i] - r0)*delta + r0
        newdata[i,1] = (data['Z'][i] - z0)*delta + z0
    print('Changing wall size...')
    return newdata


if __name__ == '__main__':
    helpList = ['-h', '-help', '--h', '--help']
    if sys.argv[1] in helpList:
        print('\nCall this function with gfile (input) and stlfile (output) absolute paths')
        print('Example:')
        print('python3 stlFromGfile.py /home/user/g000001.00001 /home/user/newSTL.stl ')
        print('Edit gfile2STL function inputs to change parameters before running')
        sys.exit()
    else:
        gfile = str(sys.argv[1])
        stlfile = str(sys.argv[2])

    gfile2STL(gfile=gfile, stlfile=stlfile)
