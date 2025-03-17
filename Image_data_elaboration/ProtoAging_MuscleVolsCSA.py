# Script to compute muscle volumes and CSAs - ForceLoss study

#--------------------------------------------------------------------------------------------
# Author: Giorgio Davico
# Year: 2022
#--------------------------------------------------------------------------------------------

# Inputs: 
	# 1. One folder per subject including:
        # a. STL file of segmented muscles (e.g. 'FRE/FRE01/MRI/vasmed_r.stl') - full segmentations

# List of operations:
	# 1. Loop through subjects
	# 2. Load muscles' STLs
    # 3. Get Muscle volume
    # 3. Identify top- and bottom-most points (origin and insertion)
	# 4. Identify cutting levels (from muscle origin to insertion, with an increment between slices = 5% of the muscle length [origin-to-insertion]; 18 slices in total)
	# 5. Create cutting planes (perpendicular to line connecting origin and insertion)
	# 6. Extract max CSA among all CSAs
	# 8. Save values (volume and max CSAs) in pandas frame
    # 9. Export results to csv file

#--------------------------------------------------------------------------------------------
    
# Import the required libraries
import os	
import numpy as np
from numpy import array
import vtk
from math import sqrt
import stl
from scipy.io import savemat
from itertools import islice
import time
import pandas as pd
from vedo import *

def get_CSA_Vol(datapath, muscName, flag, inDir, outDir, subj, sbjDF): # main function to perform a cut and save STLs
    
    print('Finding CSA for muscle: ' + muscName)
    print('----------------------------')

    orig,insert,stlR,stlRpdata = getVertices(datapath)
    stlPDataPort = stlR.GetOutputPort() 

    # Get muscle origin and insertion points
    # cutPtsAll = findCutLevels(np.array(orig),np.array(insert))   
    cutPtsAll = findAllCutLevels(np.array(orig),np.array(insert))   

    
    sbjCSA = []
    for j,cutPts in enumerate(cutPtsAll):
        myCSA = getCSA(Mesh(datapath),np.array(insert),np.array(orig),cutPts) #getCSA(check,myContour,mySlice)
        sbjCSA.append(myCSA)   

    # find max CSA
    maxCSA = np.max(sbjCSA)

    musclePart =  stl.mesh.Mesh.from_file(datapath) # trimesh.load(A)
    muscleVol = musclePart.get_mass_properties()[0] # partA.volume 
    mVol = float(muscleVol/1000)   
    # update pandas df with CSA values and muscle volume for current patient
    sbjDF = populateRedDict(sbjDF,muscName,mVol,maxCSA)


    #save dictionary as Excel file
    fileVolCSV = '{}_muscle_volumes.csv'.format(subj)
    csvpath = os.path.join(outDir,fileVolCSV)
    save2csv(csvpath, sbjDF)

    print ('\nCSAs and volume computed for muscle: ' + muscName)
    # print('\nMid,Bot,Top CSA: {} mm\u00b2'.format(sbjCSA))
    print('Max CSA: {} mm\u00b2'.format(maxCSA))
    # print('Mean CSA: {} mm\u00b2'.format(avgCSA))
    print('Muscle volume: {} cm\u00b3\n'.format(mVol))
    print('----------------------------')

def getVertices(stl): # function to get the vertices from the original STL
    stlReader = vtk.vtkSTLReader()
    stlReader.SetFileName(stl)
    stlReader.ScalarTagsOn()
    stlReader.Update()
    # # Get polydata from STL file 
    stlPolyData = stlReader.GetOutput()
    n_points = stlPolyData.GetNumberOfPoints()
    vertices = np.zeros([n_points, 3])
    for i in range(n_points):
        vertices[i][0], vertices[i][1], vertices[i][2] = stlPolyData.GetPoint(i)
    # find indices for max and min points
    zList = [m[2] for ii,m in enumerate(vertices)]
    maxPt = zList.index(max(zList))
    minPt = zList.index(min(zList))
    # get origin and insertion
    origin = np.zeros([1, 3])
    origin[0][0],origin[0][1],origin[0][2] = stlPolyData.GetPoint(maxPt)
    insertion = np.zeros([1, 3])
    insertion[0][0],insertion[0][1],insertion[0][2] = stlPolyData.GetPoint(minPt)
    return origin, insertion, stlReader, stlPolyData

def findAllCutLevels(oPoint,iPoint):
    lenMusc = (oPoint-iPoint)
    # curPt = oPoint
    increment = 0.05
    allCutPoints = []
    for iPt in range(1,18,1): # not calculating the CSA in correspodence of origin and insertion points
        p1 = oPoint-lenMusc*increment*(iPt+1)
        allCutPoints.append(p1)
    return allCutPoints

def findCutLevels(oPoint,iPoint): # function to identify where to perform the cuts
    # measure length
    lenMusc = (oPoint-iPoint)
    # move along line and stop midway
    midPt = (oPoint+iPoint)/2
    cutPoints = []
    cutPoints.append(midPt)
    percentCut = 0.05 # i.e., 10% more and less than midpoint
    # of a percentCut above midpoint
    p1 = midPt-lenMusc*percentCut
    cutPoints.append(p1)
    # same distance below the midpoint
    p2 = midPt+lenMusc*percentCut 
    cutPoints.append(p2)
    return cutPoints

def findCSA(mySTLpd,oPt,iPt,cPt):
    # create cut plane
    lineVec = unitVec(iPt,oPt)
    plane = vtk.vtkPlane()
    plane.SetOrigin(cPt[0][0], cPt[0][1], cPt[0][2])
    plane.SetNormal(lineVec[0],lineVec[1],lineVec[2])
    # create cutter
    cutEdges = vtk.vtkCutter()
    cutEdges.SetInputConnection(mySTLpd)
    cutEdges.SetCutFunction(plane)
    cutEdges.GenerateCutScalarsOn()
    cutEdges.SetValue(0, 0.5)
    cutStrips = vtk.vtkStripper()
    cutStrips.SetInputConnection(cutEdges.GetOutputPort())
    cutStrips.Update()
    # get polydata intersection (plane vs stl)
    cutPoly = vtk.vtkPolyData()
    cutPoly.SetPoints(cutStrips.GetOutput().GetPoints())
    cutPoly.SetPolys(cutStrips.GetOutput().GetLines())

    return cutEdges, cutPoly, cutStrips

def getCSA(mySTL,iPt,oPt,cPt): #getCSA(cutPl,contour, MagicM)

    msh = mySTL.scale(1).shift(-cPt[0][0], -cPt[0][1], -cPt[0][2])
    plane = Grid(resx=100, resy=100).wireframe(False).scale(200)
    
    ## possible alternative
    # lineVec = unitVec(iPt,oPt)
    # plane = Plane(pos=(cPt[0][0], cPt[0][1], cPt[0][2]), normal=(0,0,1), sx=200, sy=200)

    cutplane = plane.clone().cutWithMesh(msh).triangulate()
    csa = cutplane.area()

    return csa

def unitVec(vecA,vecB):
    add = 0
    connects = []
    for i in range(0, 3):
        unit = 0
        connect = vecB[0][i] - vecA[0][i]
        connects.append(connect)
        add = add + (connect**2)
    uVec = sqrt(add)
    unitV = [val/uVec for val in connects]
    return unitV
 
def initRedDict():
    genRDict = {}
    genRDict['muscle'],genRDict['volume (cm3)'],genRDict['csa_max (mm2)'] = [],[],[]
    return genRDict

def populateRedDict(gDictR,myMuscle,myVol,myCSAmid):
    gDictR['muscle'].append(myMuscle)
    gDictR['volume (cm3)'].append(myVol)
    gDictR['csa_max (mm2)'].append(myCSAmid)
    return gDictR

def save2csv(filename,myDict):
    df = pd.DataFrame.from_dict(myDict)
    df.to_csv(filename)
   
start_time_init = time.time()
   
basepath = 'E:/Proto-Aging/Data_Collection/'
rawSegPath = os.path.join(basepath,'HYA/')

subjects = next(os.walk(rawSegPath))[1]

for sub in subjects:
    start_time_sbj = time.time()
    print ('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print ('Working on Subject: ' + sub)
    print ('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    spath = os.path.join(rawSegPath,sub)
    subpath = os.path.join(spath,'MRI')

    muscMRI = [file for file in next(os.walk(subpath))[2] if file.endswith('.stl')]
    flag = []
    # sbjDF = initDict()
    sbjDF = initRedDict()
    for musc in muscMRI:
        muscN = musc[:-4]
        stlFile = os.path.join(subpath,musc)  
        flag = muscN[0]
        muscN_short = muscN[6:]
        # perform cut and save stl
        get_CSA_Vol(stlFile, muscN_short, flag, subpath, subpath, sub, sbjDF)
            
    elapsed_time_sbj = time.time() - start_time_sbj
    print('\n')
    print('Subject {} analyzed in {} s'.format(sub,elapsed_time_sbj))
    print('\n')

    elapsed_time_tot = time.time() - start_time_init
    print('~~~~~~~~~~~~~~~~END~~~~~~~~~~~~~~~')
    print('\nAnalysis completed in: {} s \n'.format(elapsed_time_tot))