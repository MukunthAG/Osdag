import ifcopenshell as ifcops

def get_attr(name):
        import pprint as pp
        schema = ifcops.ifcopenshell_wrapper.schema_by_name("IFC2X3")
        ele = schema.declaration_by_name(name)
        pp.pprint(ele.all_attributes())
    
get_attr("IfcColumn")