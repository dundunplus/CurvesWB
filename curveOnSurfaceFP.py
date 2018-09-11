# -*- coding: utf-8 -*-

__title__ = "Curve on surface"
__author__ = "Christophe Grellier (Chris_G)"
__license__ = "LGPL 2.1"
__doc__ = "Creates a parametric curve on surface object."

import FreeCAD
import FreeCADGui
import Part
import curveOnSurface
from FreeCAD import Base
import _utils

TOOL_ICON = _utils.iconsPath() + '/curveOnSurface.svg'
debug = _utils.debug
#debug = _utils.doNothing

class cosFP:
    """Creates a parametric curve on surface object."""
    def __init__(self, obj):
        ''' Add the properties '''
        obj.addProperty("App::PropertyLinkSub",    "InputEdge",      "CurveOnSurface",   "Input edge")
        obj.addProperty("App::PropertyLinkSub",    "Face",           "CurveOnSurface",   "Support face")
        obj.addProperty("App::PropertyFloat",      "Tolerance",      "CurveOnSurface",   "Tolerance").Tolerance=0.0001
        obj.addProperty("App::PropertyBool",       "ReverseTangent", "Orientation",   "Reverse tangent").ReverseTangent = False
        obj.addProperty("App::PropertyBool",       "ReverseNormal",  "Orientation",   "Reverse normal").ReverseNormal = False
        obj.addProperty("App::PropertyBool",       "ReverseBinormal","Orientation",   "Reverse binormal").ReverseBinormal = False
        #obj.addProperty("Part::PropertyPartShape", "Shape",          "Base",   "Shape")
        obj.addProperty("App::PropertyEnumeration","Output",         "CurveOnSurface",   "Output type").Output = ["Curve only","Normal face","Binormal face"]
        obj.addProperty("App::PropertyInteger",    "Samples",        "CurveOnSurface", "Number of samples").Samples=100
        obj.addProperty("App::PropertyDistance",   "FaceWidth",      "CurveOnSurface", "Width of the output face").FaceWidth='1mm'
        obj.addProperty("App::PropertyBool",       "Symmetric",      "CurveOnSurface", "Face symmetric across curve").Symmetric = False
        obj.addProperty("App::PropertyBool",       "Closed",         "CurveOnSurface", "Close the curve").Closed = False
        obj.Output = "Curve only"
        obj.Proxy = self

    def onChanged(self, fp, prop):
        if prop == "Samples":
            if fp.Samples < 3:
                fp.Samples = 3
            elif fp.Samples > 1000:
                fp.Samples = 1000
        if prop == "FaceWidth":
            if abs(fp.FaceWidth) < 1e-5:
                fp.FaceWidth = 1e-5
            #elif fp.FaceWidth > 1000:
                #fp.FaceWidth = 1000

    def execute(self, obj):
        edge = _utils.getShape(obj, 'InputEdge', 'Edge') # self.getEdge(obj)
        face = _utils.getShape(obj, 'Face', 'Face') # self.getFace(obj)
        cos = curveOnSurface.curveOnSurface(edge, face)
        if obj.Closed:
            cos.closed = True
        cos.reverseTangent = obj.ReverseTangent
        cos.reverseNormal = obj.ReverseNormal
        cos.reverseBinormal = obj.ReverseBinormal
        if obj.Output == "Normal face":
            obj.Shape = cos.normalFace(obj.Samples, float(obj.FaceWidth), obj.Tolerance, obj.Symmetric)
        elif obj.Output == "Binormal face":
            obj.Shape = cos.binormalFace(obj.Samples, float(obj.FaceWidth), obj.Tolerance, obj.Symmetric)
        else:
            obj.Shape = cos.edgeOnFace

class cosVP:
    def __init__(self,vobj):
        vobj.Proxy = self

    def getIcon(self):
        return(TOOL_ICON)

    def attach(self, vobj):
        self.Object = vobj.Object

    def __getstate__(self):
        return({"name": self.Object.Name})

    def __setstate__(self,state):
        self.Object = FreeCAD.ActiveDocument.getObject(state["name"])
        return(None)

    def claimChildren(self):
        return [self.Object.InputEdge[0]]

    def onDelete(self, feature, subelements):
        try:
            self.Object.InputEdge[0].ViewObject.Visibility=True
        except Exception as err:
            App.Console.PrintError("Error in onDelete: " + err.message)
        return(True)



class cosCommand:
    """Creates a parametric curve on surface object."""
    def Activated(self):
        edge = None
        face = None
        sel = FreeCADGui.Selection.getSelectionEx()
        if sel == []:
            FreeCAD.Console.PrintError("Select an edge and its supporting face \n")
        for selobj in sel:
            if selobj.HasSubObjects:
                for i in range(len(selobj.SubObjects)):
                    if isinstance(selobj.SubObjects[i], Part.Edge):
                        edge = (selobj.Object, selobj.SubElementNames[i])
                        selobj.Object.ViewObject.Visibility = False
                    elif isinstance(selobj.SubObjects[i], Part.Face):
                        face = (selobj.Object, selobj.SubElementNames[i])
        #debug(edge)
        #debug(face)
        if edge and face:
            cos = FreeCAD.ActiveDocument.addObject("Part::FeaturePython","CurveOnSurface")
            cosFP(cos)
            cos.InputEdge = edge
            cos.Face = face
            #cos.Placement = edge[0].Placement
            cosVP(cos.ViewObject)
            FreeCAD.ActiveDocument.recompute()

            #cos.ViewObject.DrawStyle = "Dashed"
            #cos.ViewObject.LineColor = (1.0,0.67,0.0)
            #cos.ViewObject.LineWidth = 3.0
        else:
            FreeCAD.Console.PrintError("Select an edge and its supporting face \n")


    def GetResources(self):
        return {'Pixmap' : TOOL_ICON, 'MenuText': 'CurveOnSurface', 'ToolTip': 'Create a curve on surface object'}

FreeCADGui.addCommand('cos', cosCommand())
