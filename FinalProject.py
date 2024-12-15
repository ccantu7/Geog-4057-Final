import arcpy
import json
import os

def importNoTaxJSON(workspace=r'c:\Users\carol\Documents\Geog 4057 Final', json_file='no_tax.json', out_fc='notax_fc_1.shp'):

    with open(json_file,'r') as file:
        tax_json = json.load(file)

    ## Covnverting the WKT to polygons
    arcpy.FromWKT(tax_json['data'][8][8]) 
    for row in tax_json['data']:
        row[8] = arcpy.FromWKT (row[8]) 


    ## Creating the feature class and write fields
    fcname = out_fc

    fc_fullname = os.path.join(workspace, fcname)
    ## Checking if file already exists so a duplicate is not created
    if arcpy.Exists(fc_fullname):
        arcpy.management.Delete(fc_fullname)

    arcpy.management.CreateFeatureclass(out_path=workspace, out_name=fcname, geometry_type='POLYGON', spatial_reference=4236)

    # Finding each field and defining its type
    fields = tax_json['meta']['view']['columns']
    field_type = ['TEXT', 'TEXT', 'LONG', 'LONG', 'TEXT', 'LONG', 'TEXT', 'TEXT', 'TEXT','TEXT','TEXT','TEXT','TEXT',]
    field_names=[]
    for ind,field in enumerate(fields):
        name = field['name']
        # Exluding the polygon field
        if name == 'the_geom':
            continue
        # Preventing repeat names
        if name.lower() == 'id':
            name = f'id_{ind}'
        max_len = min(10,len(name))
        name = name[:max_len]
        field_names.append(name)
    # Removing spaces and periods from names 
    field_names = [field.replace(" ","_") for field in field_names]
    field_names = [field.replace(".","_") for field in field_names]
    field_names

    for ind,field_name in enumerate(field_names):
        arcpy.management.AddField(fc_fullname,field_name=field_name,field_type=field_type[ind])
    field_names.append('SHAPE@')

    ## Writing data to a feature class
    with arcpy.da.InsertCursor(fc_fullname,field_names=field_names) as cursor:
        for row in tax_json['data']:
            new_row = []
            for ind, value in enumerate(row):
                if ind == 8:
                    continue
                if value == None:
                    value = ''
                new_row.append(value)
            new_row.append(row[8])
            cursor.insertRow(new_row)

