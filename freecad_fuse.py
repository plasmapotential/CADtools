#freecad_fuse.py
#Description:   Fuses all parts in freecad
#Engineer:      T. Looby
#Date:          20190925

FREECADPATH = '/usr/lib64/freecad/lib'
FREECADPATH = '/usr/lib64/freecad/lib'
import sys
sys.path.append(FREECADPATH)
import FreeCAD
import FreeCADGui as Gui




#Select all objects in GUI
def selectall():
    Gui.Selection.clearSelection()
    for obj in FreeCAD.ActiveDocument.Objects:
        if obj.ViewObject.isVisible():
            Gui.Selection.addSelection(obj)

def getAllNames():
    print('Getting Names...')
    objects = []
    names = []
    #Get all objects by name
    for obj in FreeCAD.ActiveDocument.Objects:
        names.append(obj.Name)
    return names

def getAllObjs():
    print('Getting Objects')
    objects = []
    #Get all objects
    for obj in FreeCAD.ActiveDocument.Objects:
        objects.append(obj)
    return objects

#Fuse all objects
def fuse(fusion_name, objects_list):
    print('Fusing...')
    fusor = FreeCAD.activeDocument().addObject("Part::MultiFuse",fusion_name)
    fusor.Shapes = objects_list
    return fusor

#Color fused stuff
def color_fused(fusor_object, shape_objects):
    print("GUI Stuff for fusor obj")
    #Get fusor GUI Object
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(fusor_object)
    gui_fusor = Gui.ActiveDocument.ActiveObject
    #Get Part / Shape Gui object
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(shape_objects[0])
    gui_shape = Gui.ActiveDocument.ActiveObject

    #Assign shape color and Display Mode Based Upon the original shape
    gui_fusor.ShapeColor = gui_shape.ShapeColor
    gui_fusor.DisplayMode = gui_shape.DisplayMode
    #Toggle Visibility for all Shapes in Fusor Object
    for obj in shape_objects:
        Gui.ActiveDocument.getObject(obj.Name).Visibility = False


def fuse_all_objects(infile, outfile):
    objs = getAllObjs()
    fusor = fuse('FUSION_OBJ', objs)
    color_fused(fusor, objs)
    #print('Recomputing...')
    #FreeCAD.ActiveDocument.recompute()
    #Save
    print('Saving...')
    FreeCAD.getDocument("test_fusion").saveAs(outfile)



if __name__ == '__main__':
    infile = '/home/tlooby/NSTX/CAD/test_PFC_horizon.fcstd'
    outfile = '/home/tlooby/NSTX/CAD/test_fusion_out.fcstd'
    print("Running FreeCAD Application...")

    FreeCAD.open(infile)
    FreeCAD.setActiveDocument("test_PFC_horizon")
    FreeCAD.ActiveDocument=FreeCAD.getDocument("test_PFC_horizon")
    Gui.showMainWindow()
    #Gui.setupWithoutGUI()
    Gui.exec_loop()
    Gui.ActiveDocument=Gui.getDocument("test_PFC_horizon.fcstd")
    fuse_all_objects(infile, outfile)




#Example to Fuse two objects
#App.activeDocument().addObject("Part::MultiFuse","TESTFUSION")
#App.activeDocument().TESTFUSION.Shapes = [App.activeDocument().Part__Feature2963,App.activeDocument().Part__Feature2998]
#Gui.ActiveDocument.TESTFUSION.ShapeColor=Gui.ActiveDocument.Part__Feature2963.ShapeColor
#Gui.ActiveDocument.TESTFUSION.DisplayMode=Gui.ActiveDocument.Part__Feature2963.DisplayMode
#Gui.activeDocument().Part__Feature2963.Visibility=False
#Gui.activeDocument().Part__Feature2998.Visibility=False
#App.ActiveDocument.recompute()


#Do this in freecad terminal to fuse entire assembly:

#objects = []
#for obj in FreeCAD.ActiveDocument.Objects:
#     objects.append(obj)
#fusor = FreeCAD.activeDocument().addObject("Part::MultiFuse","FUSION_OBJ")
#fusor.Shapes = objects
#Gui.ActiveDocument.FUSION_OBJ.ShapeColor=Gui.ActiveDocument.Part__Feature2963.ShapeColor
#Gui.ActiveDocument.FUSION_OBJ.DisplayMode=Gui.ActiveDocument.Part__Feature2963.DisplayMode
#for obj in objects:
#    Gui.ActiveDocument.getObject(obj.Name).Visibility = False
