# Update Data Tracker location records with council district, engineer area,
# and jurisdiction attributes from from COA ArcGIS Online feature services

# Attributes
# ----------
# field_maps : TYPE
#     Description
# filters : TYPE
#     Description
# knack_creds : TYPE
#     Description
# layers : TYPE
#     Description
# obj : str
#     Description
import argparse
import os
import pdb
import traceback

import arrow
import knackpy

import _setpath
from config.secrets import *
from tdutils import agolutil
from tdutils import argutil
from tdutils import datautil
from tdutils import emailutil
from tdutils import jobutil
from tdutils import logutil

knack_creds = KNACK_CREDENTIALS
obj = "object_11"

field_maps = {
    #  service name
    "EXTERNAL_cmta_stops": {
        "fields": {
            #  AGOL Field : Knack Field
            "ID": "BUS_STOPS"
        }
    }
}

layers = [
    {
        "service_name": "BOUNDARIES_single_member_districts",
        "outFields": "COUNCIL_DISTRICT",
        "updateFields": ["COUNCIL_DISTRICT"],  #
        "layer_id": 0,
        "distance": 33,  #  !!! this unit is interpreted as meters due to Esri bug !!!
        "units": "esriSRUnit_Foot",  #  !!! this unit is interpreted as meters due to Esri bug !!!
        #  how to handle query that returns multiple intersection features
        "handle_features": "merge_all",
    },
    {
        "service_name": "BOUNDARIES_jurisdictions",
        #  will attempt secondary service if no results at primary
        "service_name_secondary": "BOUNDARIES_jurisdictions_planning",
        "outFields": "JURISDICTION_LABEL",
        "updateFields": ["JURISDICTION_LABEL"],
        "layer_id": 0,
        "handle_features": "use_first",
    },
    {
        "service_name": "ATD_signal_engineer_areas",
        "outFields": "SIGNAL_ENG_AREA",
        "updateFields": ["SIGNAL_ENG_AREA"],
        "layer_id": 0,
        "handle_features": "use_first",
    },
    {
        "service_name": "EXTERNAL_cmta_stops",
        "outFields": "ID",
        "updateFields": ["BUS_STOPS"],
        "layer_id": 0,
        "distance": 107,  #  !!! this unit is interpreted as meters due to Esri bug !!!
        "units": "esriSRUnit_Foot",  #  !!! this unit is interpreted as meters due to Esri bug !!!
        "handle_features": "merge_all",
        "apply_format": format_stringify_list,
    },
]

filters = {
    #  filter for records where
    #  UPDATE_PROCESSED field is No
    "match": "and",
    "rules": [{"field": "field_1357", "operator": "is", "value": "No"}],
}

def format_stringify_list(input_list):
    """
    Function to format features when merging multiple feature attributes
    
    Parameters
    ----------
    input_list : TYPE
        Description
    
    Returns
    -------
    TYPE
        Description
    """
    return ", ".join(str(l) for l in input_list)


# layer config for interacting with ArcGIS Online
# see: http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#//02r3000000p1000000




def map_fields(record, field_map):
    """
    Replace field names according to field map. Used to replace ArcGIS Online
    reference feature service field names with database field names.
    
    Parameters
    ----------
    record : TYPE
        Description
    field_map : TYPE
        Description
    
    Returns
    -------
    TYPE
        Description
    """
    new_record = {}

    for field in record.keys():
        outfield = field_map["fields"].get(field)

        if outfield:
            new_record[outfield] = record[field]
        else:
            new_record[field] = record[field]

    return new_record


def get_params(layer_config):
    """base params for AGOL query request
    
    Parameters
    ----------
    layer_config : TYPE
        Description
    
    Returns
    -------
    TYPE
        Description
    """
    params = {
        "f": "json",
        "outFields": "*",
        "geometry": None,
        "geomtryType": "esriGeometryPoint",
        "returnGeometry": False,
        "spatialRel": "esriSpatialRelIntersects",
        "inSR": 4326,
        "geometryType": "esriGeometryPoint",
        "distance": None,
        "units": None,
    }

    for param in layer_config:
        if param in params:
            params[param] = layer_config[param]

    return params


def join_features_to_record(features, layer_config, record):
    """'
    Join feature attributes from ArcGIS Online query to location record
    
    Parameters
    ----------
    features : list (required)
        The 'features' array from an Esri query response object.
        See see: http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#//02r3000000p1000000
    layer_config : dict (required)
        The layer configuration dict that was provided to the ArcGIS Online query 
        and returned the providded features.
    record : dict (required)
        The source database record whose geomtetry intersects with
        the provided features
    
    Returns
    -------
    record (dict)
        The updated record object with location attributes attached
    """
    handler = layer_config["handle_features"]

    if handler == "use_first" or len(features) == 1:
        #  use first feature in results and join feature data to location record
        feature = features[0]

        for field in feature["attributes"].keys():
            #  remove whitespace from janky Esri fields
            record[field] = str(feature["attributes"][field]).strip()

    elif handler == "merge_all" and len(features) > 1:
        #  concatenate feature attributes from each feature and join to record
        for feature in features:
            for field in feature["attributes"].keys():
                if field not in record:
                    record[field] = []

                record[field].append(str(feature["attributes"][field]).strip())

        if layer_config.get("apply_format"):
            #  apply special formatting function to attribute array
            for field in feature["attributes"].keys():
                input_val = record[field]
                record[field] = layer_config["apply_format"](input_val)

    return record


def cli_args():
    """Summary
    
    Returns
    -------
    TYPE
        Description
    """
    parser = argutil.get_parser(
        "location_updater.py",
        "Update location attributes via point-in-poly against various intersecting geospatial data layers.",
        "app_name",
    )

    args = parser.parse_args()

    return args


def main(job, **kwargs):
    """
    Knack database fields that will be updated. Payload is reduced to
    these fields.
    
    Parameters
    ----------
    job : TYPE
        Description
    **kwargs
        Description
    
    Returns
    -------
    TYPE
        Description
    
    Raises
    ------
    Exception
        Description
    """

    script_name = kwargs["script_name"]
    app_name = kwargs["app_name"]

    update_fields = [field for layer in layers for field in layer["updateFields"]]

    kn = knackpy.Knack(
        obj=obj,
        app_id=KNACK_CREDENTIALS[app_name]["app_id"],
        api_key=KNACK_CREDENTIALS[app_name]["api_key"],
        filters=filters,
        timeout=30,
    )

    unmatched_locations = []

    if not kn.data:
        return 0

    """
    Remove "update fields" from record. these are re-appended via
    spatial lookup and thus the fieldnames must match those of the source
    dataset or be mapped in the field map config dict.
    """
    keep_fields = [field for field in kn.fieldnames if field not in update_fields]
    kn.data = datautil.reduce_to_keys(kn.data, keep_fields)

    for location in kn.data:

        point = [location["LOCATION_longitude"], location["LOCATION_latitude"]]

        for layer in layers:
            layer["geometry"] = point
            field_map = field_maps.get(layer["service_name"])
            params = get_params(layer)

            try:
                res = agolutil.point_in_poly(
                    layer["service_name"], layer["layer_id"], params
                )

                if res.get("error"):
                    raise Exception(str(res))

                if res.get("features"):
                    location = join_features_to_record(res["features"], layer, location)

                    if field_map:
                        location = map_fields(location, field_map)

                    continue

                if "service_name_secondary" in layer:
                    res = agolutil.point_in_poly(
                        layer["service_name_secondary"], layer["layer_id"], params
                    )

                    if len(res["features"]) > 0:
                        location = join_features_to_record(
                            res["features"], layer, location
                        )

                        if field_map:
                            location = map_fields(location, field_map)
                            continue

                #  no intersecting features found
                for field in layer["updateFields"]:
                    """
                    set corresponding fields on location record to null to
                    overwrite any existing data
                    """
                    location[field] = ""

                continue

            except Exception as e:
                unmatched_locations.append(location)
                continue

        location["UPDATE_PROCESSED"] = True
        location["MODIFIED_DATE"] = datautil.local_timestamp()

        location = datautil.reduce_to_keys(
            [location], update_fields + ["id", "UPDATE_PROCESSED", "MODIFIED_DATE"]
        )
        location = datautil.replace_keys(location, kn.field_map)

        res = knackpy.record(
            location[0],
            obj_key=obj,
            app_id=KNACK_CREDENTIALS[app_name]["app_id"],
            api_key=KNACK_CREDENTIALS[app_name]["api_key"],
            method="update",
        )

    # logger.info('{} records updated'.format( len(kn.data) - len(
    # unmatched_locations)))

    if len(unmatched_locations) > 0:
        error_text = "Location Point/Poly Match Failure(s): {}".format(
            ", ".join(str(x) for x in unmatched_locations)
        )
        raise Exception(error_text)

    else:
        return len(kn.data)
