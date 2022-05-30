from IfcGeometry import *

TIME = time.time()
PROJECTNAME = "Column"

class ColumnBase(IfcGeometry):
    """
    A square shaped column base of square width "w" and height "h"
    """
    def __init__(self, base_params, **kwargs):
        bp = base_params
        super().__init__(**kwargs)
        """
        Creating a Local Coordinate System at (5,5,0) with Pure Translation

        Y
        ^
        |
        |
        |---------------(5.,5.,0.) => ColumnBase's LCS will be placed here
        |               |
        |               |
        |               |
        |               |
        |               |
        |--------------------------- > X  ==> Storey's LCS (Local Coordinate System)

        """
        self.base_location = bp.get("base_location")
        self.w = bp.get("base_width")
        self.h = bp.get("base_height")
        self.base_local_placement = self.create_ifclocalplacement(point = self.base_location, relative_to = self.storey_placement)
        self.construct_base_profile2d()
        self.extrude_base_profile()
        self.base_product_representation = self.create_product_representation(self.extruded_base)
        self.base_product_as_ifccolumn()

    def construct_base_profile2d(self):
        self.base_profile_placement = self.ifcfile.createIfcAxis2Placement2D(self.ori, self.Xdir)
        self.base_profile = self.ifcfile.createIfcRectangleProfileDef("AREA", "Column Base Profile", self.base_profile_placement, self.w, self.w)
    
    def extrude_base_profile(self):
        self.extruded_base = self.ifcfile.createIfcExtrudedAreaSolid(self.base_profile, self.g_placement, self.Zdir, self.h)
    
    def base_product_as_ifccolumn(self):
        params = {
            "GlobalId": self.guid(),
            "Name": "Column Base",
            "OwnerHistory": self.owner_history,
            "ObjectPlacement": self.base_local_placement,
            "Representation": self.base_product_representation
        }
        self.base_as_ifccolumn = self.ifcfile.createIfcColumn(**params)
        params = {
            "GlobalId": self.guid(),
            "OwnerHistory": self.owner_history,
            "RelatedElements": [self.base_as_ifccolumn],
            "RelatingStructure": self.building_storey
        }
        self.ifcfile.createIfcRelContainedInSpatialStructure(**params)

class Column(ColumnBase):
    def __init__(self, column_params, base_params, **kwargs):
        self.column_params = column_params
        super().__init__(base_params, **kwargs)
        col_foot = float(base_params.get("base_height"))
        self.column_local_placement = self.create_ifclocalplacement(point = (0.,0.,col_foot), relative_to = self.base_local_placement)
        self.construct_column_profile2d()
        self.extrude_column_profile()
        self.column_product_representation = self.create_product_representation(self.extruded_column)
        self.column_product_as_ifccolumn()

    def construct_column_profile2d(self):
        self.column_profile_placement = self.ifcfile.createIfcAxis2Placement2D(self.ori, self.Xdir)
        self.col_height = self.column_params.get("ColumnHeight")
        self.column_params.pop("ColumnHeight")
        self.column_profile = self.ifcfile.createIfcIShapeProfileDef("AREA", "Column Profile", self.column_profile_placement, **self.column_params)
    
    def extrude_column_profile(self):
        self.extruded_column = self.ifcfile.createIfcExtrudedAreaSolid(self.column_profile, self.g_placement, self.Zdir, self.col_height)

    def column_product_as_ifccolumn(self):
        params = {
            "GlobalId": self.guid(),
            "Name": "Column",
            "OwnerHistory": self.owner_history,
            "ObjectPlacement": self.column_local_placement,
            "Representation": self.column_product_representation
        }
        self.column_as_ifccolumn = self.ifcfile.createIfcColumn(**params)
        params = {
            "GlobalId": self.guid(),
            "OwnerHistory": self.owner_history,
            "RelatedElements": [self.column_as_ifccolumn],
            "RelatingStructure": self.building_storey
        }
        self.ifcfile.createIfcRelContainedInSpatialStructure(**params)
        
column_params = {
    "OverallWidth": 0.6,
    "OverallDepth": 0.75,
    "WebThickness": 0.05,
    "FlangeThickness": 0.05,
    "FilletRadius": 0.05,
    "ColumnHeight": 5
}

base_params = {
    "base_location": (5., 5., 0.),
    "base_width": 1.,
    "base_height": 1.5
}

CONFIG = {
    "filename": PROJECTNAME + ".ifc",
    "timestamp": TIME,
    "timestring": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(TIME)),
    "creator": "Mukunth A G",
    "organization": "IIT Bombay",
    "application": "IfcOpenShell", 
    "application_version": "0.7.0-1b1fd1e6",
    "project_globalid": ifcops.guid.new(), 
    "project_name": PROJECTNAME + "Osdag",
}

column_obj = Column(column_params, base_params, **CONFIG)

column_obj.ifcfile.write("Samples/" + PROJECTNAME + ".ifc")