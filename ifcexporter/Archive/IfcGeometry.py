'''
DEPRECEATED
'''

from IfcInitializer import *

O = (0., 0., 0.)
X = (1., 0., 0.)
Y = (0., 1., 0.)
Z = (0., 0., 1.)

class IfcGeometry(IfcObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def create_point(self, point):
        if point == O:
            point = self.ori
        else:
            point = self.ifcfile.createIfcCartesianPoint(point)
        return point
    
    def create_dir(self, dir):
        if dir == X: 
            dir = self.Xdir
        elif dir == Y: 
            dir = self.Ydir
        elif dir == Z: 
            dir = self.Zdir
        else:
            dir = self.ifcfile.createIfcDirection(dir)
        return dir

    def create_ifcaxis2placement(self, point = O, new_Zdir = Z, ref_dir = X):
        point = self.create_point(point)
        new_Zdir = self.create_dir(new_Zdir)
        ref_dir = self.create_dir(ref_dir)
        axis2placement = self.ifcfile.createIfcAxis2Placement3D(point, new_Zdir, ref_dir)
        return axis2placement

    def create_ifclocalplacement(self, point = O, new_Zdir = Z, ref_dir = X, relative_to = None):
        axis2placement = self.create_ifcaxis2placement(point, new_Zdir, ref_dir)
        ifclocalplacement2 = self.ifcfile.createIfcLocalPlacement(relative_to, axis2placement)
        return ifclocalplacement2

    def create_ifcpolyline(self,  point_list):
        ifcpts = []
        for point in point_list:
            point = self.ifcfile.createIfcCartesianPoint(point)
            ifcpts.append(point)
        polyline = self.ifcfile.createIfcPolyLine(ifcpts)
        return polyline

    def create_ifcextrudedareasolid(self,  point_list, ifcaxis2placement, extrude_dir, extrusion):
        polyline = self.create_ifcpolyline( point_list)
        ifcclosedprofile = self.ifcfile.createIfcArbitraryClosedProfileDef("AREA", None, polyline)
        ifcdir = self.ifcfile.createIfcDirection(extrude_dir)
        ifcextrudedareasolid = self.ifcfile.createIfcExtrudedAreaSolid(ifcclosedprofile, ifcaxis2placement, ifcdir, extrusion)
        return ifcextrudedareasolid

    def create_product_representation(self, extruded_body):
        shape_representation = self.ifcfile.createIfcShapeRepresentation(self.context, "Body", "SweptSolid", [extruded_body])
        product_representation = self.ifcfile.createIfcProductDefinitionShape(Representations = [shape_representation])
        return product_representation
