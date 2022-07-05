from IfcInitializer import *
from IfcCAD.ISection import ISection
from IfcCAD.Angle import Angle
import numpy as np
import json

class CleatColFlangeBeamWebConnectivity(IfcObject):
    def __init__(self, design_data, **kwgs):
        super().__init__(**kwgs)
        self.dd = design_data 
        self.fetch_data()
        self.create_and_place()
        self.create_heirarchy()
    
    def fetch_data(self):
        self.column_data = self.dd["supporting"]
        self.beam_data = self.dd["supported"]
        self.angle_data = self.dd["angle"]
        self.gap = self.dd["gap"]
    
    def create_and_place(self):
        self.create_column()
        self.create_beam()
        self.create_angle()
        self.create_angle_mirror()
    
    def create_heirarchy(self):
        self.place_ifcelement_in_storey(self.ifccolumn, self.ground_storey)
        self.place_ifcelement_in_storey(self.ifcbeam, self.ground_storey)
        self.place_ifcelement_in_storey(self.ifcplate_angle, self.ground_storey)
        self.place_ifcelement_in_storey(self.ifcplate_angle_mirror, self.ground_storey)

    def create_column(self):
        self.column = ISection(self.ifcfile, **self.column_data)
        self.column_placement = self.column.place(relative_to = self.storey_placement)
        self.ifccolumn = self.column.create_ifccolumn("Column", self.column_placement)
    
    def create_beam(self):
        self.beam = ISection(self.ifcfile, **self.beam_data)
        self.beam_placement = self.beam.place(
            relative_to = self.column_placement,
            point = j*(self.column_data["D"]/2) + k*(self.column_data["length"]/2),
            new_Zdir = j,
            ref_dir = i,
        )
        self.ifcbeam = self.beam.create_ifcbeam("Beam", self.beam_placement)

    def create_angle(self):
        self.angle = Angle(self.ifcfile, **self.angle_data)
        self.angle_placement = self.angle.place(
            relative_to = self.beam_placement,
            point = i*(self.beam_data["t"]/2) + j*(2*self.gap["gap"]),
            new_Zdir = -j
        )
        self.ifcplate_angle = self.angle.create_angle_as_ifcplate("Angle", self.angle_placement)
    
    def create_angle_mirror(self):
        self.angle_mirror_placement = self.angle.place(
            relative_to = self.beam_placement,
            point = -i*(self.beam_data["t"]/2) + j*(2*self.gap["gap"] - self.angle_data["L"]),
            new_Zdir = j,
            ref_dir = -i
        )
        self.ifcplate_angle_mirror = self.angle.create_angle_as_ifcplate("Angle Mirror", self.angle_mirror_placement)

if __name__ == "__main__":
    CONFIG = {
        "filename": "CleatTest1.ifc",
    }
    design_data = json.load(open("DesignData/CleatColFlangeBeamWebConnectivity.json"))
    CleatTest = CleatColFlangeBeamWebConnectivity(design_data, **CONFIG)
    CleatTest.write_ifcfile()