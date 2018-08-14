"""
Publish pavement markings work orders to ArcGIS Online
"""
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
from tdutils import knackutil
from tdutils import logutil


config = [
     # Knack and AGOL source object defintions.
     # Order of config elements matters! Work orders must be processed before
     # jobs and attachments because work orders are the parent record to both.
    {
        "name": "signs_markings_work_orders",
        "scene": "scene_774",
        "view": "view_2226",
        "ref_obj": ["object_140", "object_7"],
        "modified_date_field_id": "field_2150",
        "modified_date_field": "MODIFIED_DATE",
        "geometry_service_id": "a78db5b7a72640bcbb181dcb88817652",  #  street segments
        "geometry_layer_id": 0,
        "geometry_record_id_field": "SEGMENT_ID",
        "geometry_layer_spatial_ref": 102739,
        "multi_source_geometry": True,
        "primary_key": "ATD_WORK_ORDER_ID",
        "service_id": "a9f5be763a67442a98f684935d15729b",
        "layer_id": 1,
        "item_type": "layer",
    },
    {
        "name": "signs_markings_jobs",
        "scene": "scene_774",
        "view": "view_2033",
        "ref_obj": ["object_141", "object_7"],
        "modified_date_field_id": "field_2196",
        "modified_date_field": "MODIFIED_DATE",
        "geometry_service_id": "a9f5be763a67442a98f684935d15729b",  #  work orders
        "geometry_layer_id": 1,
        "geometry_record_id_field": "ATD_WORK_ORDER_ID",
        "geometry_layer_spatial_ref": 102739,
        "multi_source_geometry": False,
        "primary_key": "ATD_SAM_JOB_ID",
        "service_id": "a9f5be763a67442a98f684935d15729b",
        "layer_id": 0,
        "item_type": "layer",
    },
    {
        "name": "attachments",
        "scene": "scene_774",
        "view": "view_2227",
        "ref_obj": ["object_153"],
        "modified_date_field_id": "field_2407",
        "modified_date_field": "CREATED_DATE",
        "multi_source_geometry": False,
        "primary_key": "ATTACHMENT_ID",
        "service_id": "a9f5be763a67442a98f684935d15729b",
        "layer_id": 0,
        "item_type": "table",
        "extract_attachment_url": True,
    },
    {
        "name": ",specifications",
        "scene": "scene_774",
        "view": "view_2272",
        "ref_obj": ["object_143","object_140", "object_141"],
        "modified_date_field_id": "field_2567",
        "modified_date_field": "MODIFIED_DATE",
        "primary_key": "SPECIFICATION_ID",
        "service_id": "a9f5be763a67442a98f684935d15729b",
        "layer_id": 1,
        "item_type": "table",
    },

    {
        "name": ",materials",
        "scene": "scene_774",
        "view": "view_2273",
        "ref_obj": ["object_36", "object_140", "object_141"],
        "modified_date_field_id": "field_771",
        "modified_date_field": "MODIFIED_DATE",
        "primary_key": "TRANSACTION_ID",
        "service_id": "a9f5be763a67442a98f684935d15729b",
        "layer_id": 2,
        "item_type": "table",
    },
]


def remove_empty_strings(records):
    new_records = []
    for record in records:
        new_record = { key : record[key] for key in record.keys() if not (type(record[key]) == str and not record[key]) }
        new_records.append(new_record)
    return new_records


def append_paths(
    records,
    features,
    multi_source_geometry=False,
    path_id_field=None,
    output_field="paths",
):
    """Append path geometries from a esri polyline data source to input records.

    Input records are assumed to contain either a list stored at 'path_id_field' which
    contains an array of ids matching the input spatial features, or a singular string
    stored as 'path_id_field' which uniquely identfies a feature in the source geomtery. 
    """
    unmatched = ''

    for record in records:
        path_id = record.get(path_id_field)

        if path_id:
            paths = []

            if type(path_id) == str:
                for feature in features:
                    if path_id == feature.attributes.get(path_id_field):
                        try:
                            paths = [path for path in feature.geometry["paths"]]
                        except TypeError:
                            pass

                        record[output_field] = paths
                        break

            elif type(path_id) == list:
                for path_id in record[path_id_field]:
                    for feature in features:
                        if path_id == feature.attributes.get(path_id_field):
                            paths = paths + [path for path in feature.geometry["paths"]]

                record[output_field] = paths

            if not record.get(output_field):
                unmatched += f'{path_id_field}: {path_id}\n'

    if unmatched:
        emailutil.send_email(
            ALERTS_DISTRIBUTION,
            f'Markings AGOL: Geomtries Not Found',
            unmatched,
            EMAIL['user'],
            EMAIL['password']
        )

    return records


def filter_by_date(data, date_field, compare_date):
    return [record for record in data if record[date_field] >= compare_date]


def knackpy_wrapper(cfg, auth, obj=None, filters=None):
    return knackpy.Knack(
        obj=obj,
        scene=cfg["scene"],
        view=cfg["view"],
        ref_obj=cfg["ref_obj"],
        app_id=auth["app_id"],
        api_key=auth["api_key"],
        filters=filters,
        page_limit=10000,
    )


def cli_args():

    parser = argutil.get_parser(
        "markings_agol.py",
        "Publish Signs and Markings Work Order Data to ArcGIS Online",
        "app_name",
        "--replace",
    )

    args = parser.parse_args()

    return args


def main(job, **kwargs):


    auth = KNACK_CREDENTIALS[kwargs["app_name"]]


    records_processed = 0

    last_run_date = job.most_recent()

    if not last_run_date or kwargs["replace"]:
        # replace dataset by setting the last run date to a long, long time ago
        # replace dataset by setting the last run date to a long, long time ago
        last_run_date = "1/1/1900"
    """
    We include a filter in our API call to limit to records which have
    been modified on or after the date the last time this job ran
    successfully. The Knack API supports filter requests by date only
    (not time), so we must apply an additional filter on the data after
    we receive it.
    """
    for cfg in config:
        filters = knackutil.date_filter_on_or_after(
            last_run_date, cfg["modified_date_field_id"]
        )

        kn = knackpy_wrapper(cfg, auth, filters=filters)

        if kn.data:
            # Filter data for records that have been modifed after the last
            # job run (see comment above)
            last_run_timestamp = arrow.get(last_run_date).timestamp * 1000
            kn.data = filter_by_date(
                kn.data, cfg["modified_date_field"], last_run_timestamp
            )

        if not kn.data:
            records_processed += 0
            continue

        records = kn.data

        if cfg.get("geometry_service_id"):
            #  dataset has geomteries to be retrieved from another dataset
            if cfg.get("multi_source_geometry"):
                source_ids = datautil.unique_from_list_field(
                    records, list_field=cfg["geometry_record_id_field"]
                )

            else:
                source_ids = datautil.get_values(
                    records, cfg["geometry_record_id_field"]
                )

            where_ids = ", ".join(f"'{x}'" for x in source_ids)
            where = "{} in ({})".format(cfg["geometry_record_id_field"], where_ids)

            geometry_layer = agolutil.get_item(
                auth=AGOL_CREDENTIALS,
                service_id=cfg["geometry_service_id"],
                layer_id=cfg["geometry_layer_id"],
            )

            source_geometries = geometry_layer.query(
                where=where, outFields=cfg["geometry_record_id_field"]
            )
            
            if not source_geometries:
                raise Exception("No features returned from source geometry layer query")

            records = append_paths(
                kn.data,
                source_geometries,
                path_id_field=cfg["geometry_record_id_field"],
            )

        if cfg.get("extract_attachment_url"):
            records = knackutil.attachment_url(
                records, in_fieldname="ATTACHMENT", out_fieldname="ATTACHMENT_URL"
            )

        records = remove_empty_strings(records) # AGOL has unexepected handling of empty values
        
        update_layer = agolutil.get_item(
            auth=AGOL_CREDENTIALS,
            service_id=cfg["service_id"],
            layer_id=cfg["layer_id"],
            item_type=cfg["item_type"],
        )

        if kwargs["replace"]:
            res = update_layer.delete_features(where="1=1")
            agolutil.handle_response(res)

        else:
            """
            Delete objects by primary key. ArcGIS api does not currently support
            an upsert method, although the Python api defines one via the
            layer.append method, it is apparently still under development. So our
            "upsert" consists of a delete by primary key then add.
            """
            primary_key = cfg.get("primary_key")

            delete_ids = [record.get(primary_key) for record in records]
            delete_ids = ", ".join(f"'{x}'" for x in delete_ids)

            #  generate a SQL-like where statement to identify records for deletion
            where = "{} in ({})".format(primary_key, delete_ids)
            res = update_layer.delete_features(where=where)
            agolutil.handle_response(res)

        for i in range(0, len(records), 1000):
            adds = agolutil.feature_collection(
                records[i : i + 1000], spatial_ref=102739
            )
            res = update_layer.edit_features(adds=adds)
            agolutil.handle_response(res)
            records_processed += len(adds)

    return records_processed


if __name__ == "__main__":
    # script_name = os.path.basename(__file__).replace(".py", "")
    # logfile = f"{LOG_DIRECTORY}/{script_name}.log"
    #
    # logger = logutil.timed_rotating_log(logfile)
    # logger.info("START AT {}".format(arrow.now()))

    # args = cli_args()
    #
    # auth = KNACK_CREDENTIALS[args.app_name]

    try:
        job = jobutil.Job(
            name=script_name,
            url=JOB_DB_API_URL,
            source="knack",
            destination="agol",
            auth=JOB_DB_API_TOKEN,
        )

        job.start()

        results = main(config, job)

        job.result("success", records_processed=results)

    except Exception as e:
        error_text = traceback.format_exc()

        logger.error(error_text)

        email_subject = "Signs & Markings AGOL Pub Failure"

        emailutil.send_email(
            ALERTS_DISTRIBUTION,
            email_subject,
            error_text,
            EMAIL['user'],
            EMAIL['password']
        )

        job.result("error", message=str(e))

        raise e
