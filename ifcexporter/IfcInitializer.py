import ifcopenshell as ifcops
import time 
import tempfile

class IfcObject():
    def __init__(self, **kwargs):
        
        locals().update(kwargs)

        self.template = """ISO-10303-21;
        HEADER;
        FILE_DESCRIPTION(('ViewDefinition [CoordinationView]'),'2;1');
        FILE_NAME('%(filename)s','%(timestring)s',('%(creator)s'),('%(organization)s'),'%(application)s','%(application)s','');
        FILE_SCHEMA(('IFC2X3'));
        ENDSEC;
        DATA;
        #1=IFCPERSON($,$,'%(creator)s',$,$,$,$,$);
        #2=IFCORGANIZATION($,'%(organization)s',$,$,$);
        #3=IFCPERSONANDORGANIZATION(#1,#2,$);
        #4=IFCAPPLICATION(#2,'%(application_version)s','%(application)s','');
        #5=IFCOWNERHISTORY(#3,#4,$,.ADDED.,$,#3,#4,%(timestamp)s);
        #6=IFCDIRECTION((1.,0.,0.));
        #7=IFCDIRECTION((0.,1.,0.));
        #8=IFCDIRECTION((0.,0.,1.));
        #9=IFCCARTESIANPOINT((0.,0.,0.));
        #10=IFCAXIS2PLACEMENT3D(#9,#8,#6);
        #11=IFCGEOMETRICREPRESENTATIONCONTEXT($,'Model',3,1.E-05,#10,#7);
        #12=IFCDIMENSIONALEXPONENTS(0,0,0,0,0,0,0);
        #13=IFCSIUNIT(*,.LENGTHUNIT.,$,.METRE.);
        #14=IFCSIUNIT(*,.AREAUNIT.,$,.SQUARE_METRE.);
        #15=IFCSIUNIT(*,.VOLUMEUNIT.,$,.CUBIC_METRE.);
        #16=IFCSIUNIT(*,.PLANEANGLEUNIT.,$,.RADIAN.);
        #17=IFCMEASUREWITHUNIT(IFCPLANEANGLEMEASURE(0.017453292519943295),#16);
        #18=IFCCONVERSIONBASEDUNIT(#12,.PLANEANGLEUNIT.,'DEGREE',#17);
        #19=IFCUNITASSIGNMENT((#13,#14,#15,#18));
        #20=IFCPROJECT('%(project_globalid)s',#5,'%(project_name)s',$,$,$,$,(#11),#19);
        ENDSEC;
        END-ISO-10303-21;
        """ % locals()

        self.ifcfile = self.make_file()
        self.extract_data_from_template()
        self.create_initial_heirarchy()

    def get_attr(name):
        import pprint as pp
        schema = ifcops.ifcopenshell_wrapper.schema_by_name("IFC2X3")
        ele = schema.declaration_by_name(name)
        pp.pprint(ele.all_attributes())
    
    def make_file(self):
        _, temp_filename = tempfile.mkstemp(suffix=".ifc")
        with open(temp_filename, "w") as f:
            f.write(self.template)
        ifcfile = ifcops.open(temp_filename)
        return ifcfile 

    def extract_data_from_template(self):
        self.owner_history = self.ifcfile.by_id(5)
        self.Xdir = self.ifcfile.by_id(6)
        self.Ydir = self.ifcfile.by_id(7)
        self.Zdir = self.ifcfile.by_id(8)
        self.ori = self.ifcfile.by_id(9)
        self.g_placement = self.ifcfile.by_id(10)
        self.context = self.ifcfile.by_id(11)
        self.project = self.ifcfile.by_id(20)

    def create_initial_heirarchy(self):
        self.create_ifcsite()
        self.create_ifcbuilding()
        self.create_ifcbuildingstorey()
        self.create_ifcrelaggregates()
    
    def guid(self):
        return ifcops.guid.new()
    
    def create_ifcsite(self):
        self.site_placement = self.ifcfile.createIfcLocalPlacement(PlacementRelTo = None, RelativePlacement = self.g_placement)
        self.site_data = {
            "GlobalId": self.guid(),
            "OwnerHistory": self.owner_history,
            "Name": "DEFAULT",
            "ObjectPlacement": self.site_placement,
            "CompositionType": "ELEMENT"
        }
        self.site = self.ifcfile.createIfcSite(**self.site_data)

    def create_ifcbuilding(self):
        self.building_placement = self.ifcfile.createIfcLocalPlacement(PlacementRelTo = self.site_placement)
        self.building_data = {
            "GlobalId": self.guid(),
            "OwnerHistory": self.owner_history,
            "Name": "LoneColumn",
            "CompositionType": "ELEMENT"
        }
        self.building = self.ifcfile.createIfcBuilding(**self.building_data)

    def create_ifcbuildingstorey(self):
        self.storey_placement = self.ifcfile.createIfcLocalPlacement(PlacementRelTo = self.building_placement)
        self.buildingstorey_data = {
            "GlobalId": self.guid(),
            "OwnerHistory": self.owner_history,
            "Name": "Ground",
            "Description": "Default Ground level, Hence no Elevation",
            "CompositionType": "ELEMENT",
            "Elevation": 0.0
        }
        self.building_storey = self.ifcfile.createIfcBuildingStorey(**self.buildingstorey_data)

    def create_ifcrelaggregates(self):
        self.ifcfile.createIfcRelAggregates(self.guid(), self.owner_history, "Building Container", "Ground level to Building", self.building, [self.building_storey])
        self.ifcfile.createIfcRelAggregates(self.guid(), self.owner_history, "Site Container", "Building to Site", self.site, [self.building])
        self.ifcfile.createIfcRelAggregates(self.guid(), self.owner_history, "Project Container", "Site to Project", self.project, [self.site])
    
    def place_ifcelement_in_storey(self, ifcelement, storey):
        params = {
            "GlobalId": self.guid(),
            "OwnerHistory": self.owner_history,
            "RelatedElements": [ifcelement],
            "RelatingStructure": storey
        }
        self.ifcfile.createIfcRelContainedInSpatialStructure(**params)