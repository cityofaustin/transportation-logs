cfg = {
    "atd_visitor_log": {
        "modified_date_field": "MODIFIED_DATE",
        "modified_date_field_id": "field_48",
        "obj": None,
        "primary_key": "id",
        "scene": "scene_20",
        "view": "view_55",
        "ref_obj": ["object_1"],
        "socrata_resource_id": "tkk5-uugs",
    },
    "backup": {
        "objects": [
            "object_137",  # admin_field_meta
            "object_138",  # admin_object_meta
            "object_95",  # csr_flex_notes
            "object_67",  # quote_of_the_week
            "object_77",  # signal_id_generator
            "object_148",  # street_names
            "object_7",  # street_segments
            "object_83",  # tmc_issues
            "object_58",  # tmc_issues_DEPRECTATED_HISTORICAL_DATA_ONLY
            "object_10",  # Asset editor
            "object_19",  # Viewer
            "object_20",  # System Administrator
            "object_24",  # Program Editor
            "object_57",  # Supervisor | AMD
            "object_65",  # Technician|AMD
            "object_68",  # Quote of the Week Editor
            "object_76",  # Inventory Editor
            "object_97",  # Account Administrator
            "object_151",  # Supervisor | Signs&Markings
            "object_152",  # Technician | Signs & Markings
            "object_155",  # Contractor | Detection
        ]
    },
    "cabinets": {
        "primary_key": "CABINET_ID",
        "ref_obj": ["object_118", "object_12"],
        "modified_date_field": "MODIFIED_DATE",
        "modified_date_field_id": "field_1793",
        "obj": None,
        "scene": "scene_571",
        "view": "view_1567",
        "service_url": "http://services.arcgis.com/0L95CJ0VTaxqcmED/ArcGIS/rest/services/cabinet_assets/FeatureServer/0/",
        "service_id": "c3fd3bb177cc4291880bbe8c630ed5c4",
        "include_ids": True,
        "socrata_resource_id": "x23u-shve",
        "ip_field": None,
        "location_fields": {
            "lat": "LOCATION_latitude",
            "lon": "LOCATION_longitude",
            "location_field": "location",
        },
    },
    "cameras": {
        "include_ids": True,
        "ip_field": "CAMERA_IP",
        "location_fields": {
            "lat": "LOCATION_latitude",
            "location_field": "location",
            "lon": "LOCATION_longitude",
        },
        "modified_date_field": "MODIFIED_DATE",
        "modified_date_field_id": "field_714",
        "obj": None,
        "primary_key": "CAMERA_ID",
        "ref_obj": ["object_53", "object_11"],
        "scene": "scene_144",
        "service_url": "http://services.arcgis.com/0L95CJ0VTaxqcmED/ArcGIS/rest/services/TRANSPORTATION_traffic_cameras/FeatureServer/0/",
        "service_id": "52f2b5e51b9a4b5e918b0be5646f27b2",
        "socrata_resource_id": "b4k4-adkb",
        "status_field": "CAMERA_STATUS",
        "status_filter_comm_status": ["TURNED_ON"],
        "view": "view_395",
    },
    "detectors": {
        "primary_key": "DETECTOR_ID",
        "ref_obj": ["object_98", "object_12"],
        "modified_date_field": "MODIFIED_DATE",
        "modified_date_field_id": "field_1533",
        "obj": None,
        "scene": "scene_468",
        "view": "view_1333",
        "service_url": "https://services.arcgis.com/0L95CJ0VTaxqcmED/arcgis/rest/services/traffic_detectors/FeatureServer/0/",
        "service_id": "47d17ff3ce664849a16b9974979cd12e",
        "socrata_resource_id": "qpuw-8eeb",
        "include_ids": True,
        "ip_field": "DETECTOR_IP",
        "fetch_locations": True,
        "location_join_field": "SIGNAL_ID",
        "location_fields": {
            "lat": "LOCATION_latitude",
            "lon": "LOCATION_longitude",
            "location_field": "location",
        },
    },
    "dms": {
        "primary_key": "DMS_ID",
        "ref_obj": ["object_109", "object_11"],
        "modified_date_field": "MODIFIED_DATE",
        "modified_date_field_id": "field_1658",
        "obj": None,
        "scene": "scene_569",
        "view": "view_1564",
        "service_url": "http://services.arcgis.com/0L95CJ0VTaxqcmED/ArcGIS/rest/services/dynamic_message_signs/FeatureServer/0/",
        "service_id": "e7104494593d4a44a2529e4044ef7d5d",
        "include_ids": True,
        "socrata_resource_id": "4r2j-b4rx",
        "ip_field": "DMS_IP",
        "location_fields": {
            "lat": "LOCATION_latitude",
            "lon": "LOCATION_longitude",
            "location_field": "location",
        },
    },
    "gridsmart": {
        #  endpoint for device status check only.
        #  data publishing is handled via detectors config
        "primary_key": "DETECTOR_ID",
        "ref_obj": ["object_98", "object_12"],
        "obj": None,
        "scene": "scene_468",
        "view": "view_1791",
        "include_ids": True,
        "ip_field": "DETECTOR_IP",
        "status_field": "DETECTOR_STATUS",
        "status_filter_comm_status": ["OK", "BROKEN", "UNKNOWN"],
    },
    "hazard_flashers": {
        "primary_key": "ATD_FLASHER_ID",
        "ref_obj": ["object_110", "object_11"],
        "modified_date_field": "MODIFIED_DATE",
        "modified_date_field_id": "field_1701",
        "obj": None,
        "scene": "scene_568",
        "view": "view_1563",
        "service_url": "http://services.arcgis.com/0L95CJ0VTaxqcmED/ArcGIS/rest/services/hazard_flashers/FeatureServer/0/",
        "service_id": "6c4392540b684d598c72e52206d774be",
        "include_ids": True,
        "socrata_resource_id": "wczq-5cer",
        "ip_field": None,
        "location_fields": {
            "lat": "LOCATION_latitude",
            "lon": "LOCATION_longitude",
            "location_field": "location",
        },
    },
    "locations": {
        "obj": None,
        "ref_obj": ["object_11"],
        "modified_date_field": "MODIFIED_DATE",
        "modified_date_field_id": "field_508",
        "scene": "scene_425",
        "view": "view_1201",
        "location_fields": {
            "lat": "LOCATION_latitude",
            "lon": "LOCATION_longitude",
            "location_field": "location",
        },
    },
    "pole_attachments": {
        "primary_key": "POLE_ATTACH_ID",
        "ref_obj": ["object_120"],
        "modified_date_field": "MODIFIED_DATE",
        "modified_date_field_id": "field_1813",
        "obj": None,
        "scene": "scene_589",
        "view": "view_1597",
        "service_url": "http://services.arcgis.com/0L95CJ0VTaxqcmED/ArcGIS/rest/services/pole_attachments/FeatureServer/0/",
        "service_id": "3a5a777f780447db940534b5808d4`7",
        "include_ids": True,
        "socrata_resource_id": "btg5-ebcy",
        "ip_field": None,
        "location_fields": {
            "lat": "LOCATION_latitude",
            "lon": "LOCATION_longitude",
            "location_field": "location",
        },
    },
    "signals": {
        "include_ids": True,
        "ip_field": "CONTROLLER_IP",
        "location_fields": {
            "lat": "LOCATION_latitude",
            "lon": "LOCATION_longitude",
            "location_field": "location",
        },
        "modified_date_field": "MODIFIED_DATE",
        "modified_date_field_id": "field_205",
        "obj": None,
        "primary_key": "SIGNAL_ID",
        "ref_obj": ["object_12", "object_11"],
        "scene": "scene_73",
        "service_id": "e6eb94d1e7cc45c2ac452af6ae6aa534",
        "socrata_resource_id": "p53x-x73x",
        "status_field": "SIGNAL_STATUS",
        "status_filter_comm_status": ["TURNED_ON"],
        "view": "view_197",
    },
    "signal_requests": {
        "primary_key": "REQUEST_ID",
        "modified_date_field": "MODIFIED_DATE",
        "modified_date_field_id": "field_217",
        "obj": None,
        "scene": "scene_75",
        "view": "view_200",
        "ref_obj": ["object_11", "object_13"],
        "service_url": "http://services.arcgis.com/0L95CJ0VTaxqcmED/arcgis/rest/services/TRANSPORTATION_signal_requests/FeatureServer/0/",
        "service_id": "c8577cef82ef4e6a89933a7a216f1ae1",
        "include_ids": True,
        "location_fields": {
            "lat": "LOCATION_latitude",
            "lon": "LOCATION_longitude",
            "location_field": "location",
        },
        "socrata_resource_id": None,
    },
    "signal_request_evals": {
        "socrata_resource_id": "f6qu-b7zb",
        "fetch_locations": True,
        "location_fields": {
            "lat": "LOCATION_latitude",
            "lon": "LOCATION_longitude",
            "location_field": "location",
        },
        "location_join_field": "ATD_LOCATION_ID",
        "multi_source": True,
        "sources": [
            #  knack_data_pub.py supports merging multiple source
            #  datasets to a destination layer
            {
                # traffic signal evals
                "include_ids": True,
                "modified_date_field": "MODIFIED_DATE",
                "modified_date_field_id": "field_659",
                "obj": None,
                "primary_key": "ATD_EVAL_ID",
                "ref_obj": ["object_13", "object_27"],
                "scene": "scene_175",
                "view": "view_908",
            },
            {
                #  phb evals
                "include_ids": True,
                "modified_date_field": "MODIFIED_DATE",
                "modified_date_field_id": "field_715",
                "obj": None,
                "primary_key": "ATD_EVAL_ID",
                "ref_obj": ["object_13", "object_26"],
                "scene": "scene_175",
                "view": "view_911",
            },
        ],
    },
    "task_orders": {
        "primary_key": "TASK_ORDER",
        "ref_obj": ["object_86"],
        "obj": None,
        "scene": "scene_861",
        "view": "view_2229",
        "include_ids": True,
    },
    "traffic_reports": {
        "primary_key": "TRAFFIC_REPORT_ID",
        "modified_date_field": "TRAFFIC_REPORT_STATUS_DATE_TIME",
        "modified_date_field_id": "field_1966",
        "ref_obj": ["object_121"],
        "obj": None,
        "scene": "scene_614",
        "view": "view_1626",
        "service_id": "444c8a2b4388485283c2968bd99ddf6c",
        "include_ids": True,
        "socrata_resource_id": "dx9v-zd7x",
        "ip_field": None,
        "location_fields": {
            "lat": "LOCATION_latitude",
            "lon": "LOCATION_longitude",
            "location_field": "location",
        },
    },
    "travel_sensors": {
        "primary_key": "ATD_SENSOR_ID",
        "ref_obj": ["object_56", "object_11"],
        "modified_date_field": "MODIFIED_DATE",
        "modified_date_field_id": "field_710",
        "obj": None,
        "scene": "scene_188",
        "view": "view_540",
        "include_ids": True,
        "service_url": "https://services.arcgis.com/0L95CJ0VTaxqcmED/arcgis/rest/services/travel_sensors/FeatureServer/0/",
        "service_id": "9776d3e894a74521a7f63443f7becc7c",
        "socrata_resource_id": "6yd9-yz29",
        "ip_field": "SENSOR_IP",
        "status_field": "SENSOR_STATUS",
        "location_fields": {
            "lat": "LOCATION_latitude",
            "lon": "LOCATION_longitude",
            "location_field": "location",
        },
        "status_filter_comm_status": ["TURNED_ON"],
    },
    "signal_retiming": {
        "primary_key": "ATD_RETIMING_ID",
        "modified_date_field": "MODIFIED_DATE",
        "modified_date_field_id": "field_1257",
        "ref_obj": ["object_42", "object_45"],
        "obj": None,
        "scene": "scene_375",
        "view": "view_1063",
        "service_url": None,
        "socrata_resource_id": "g8w2-8uap",
        "include_ids": False,
    },
    "timed_corridors": {
        "primary_key": "ATD_SYNC_SIGNAL_ID",
        "modified_date_field": "MODIFIED_DATE",
        "modified_date_field_id": "field_2557",
        "ref_obj": ["object_12", "object_42", "object_43"],
        "obj": None,
        "scene": "scene_277",
        "view": "view_765",
        "service_url": None,
        "socrata_resource_id": "efct-8fs9",
        "include_ids": False,
        "fetch_locations": True,
        "location_join_field": "SIGNAL_ID",
        "location_fields": {
            "lat": "LOCATION_latitude",
            "lon": "LOCATION_longitude",
            "location_field": "location",
        },
    },
    "work_orders_signals": {
        "primary_key": "ATD_WORK_ORDER_ID",
        "modified_date_field": "MODIFIED_DATE",
        "modified_date_field_id": "field_1074",
        "obj": None,
        "scene": "scene_683",
        "view": "view_1829",
        "ref_obj": ["object_31", "object_11"],
        "socrata_resource_id": "hst3-hxcz",
        "status_field": "WORK_ORDER_STATUS",
        "location_fields": {
            "lat": "LOCATION_latitude",
            "lon": "LOCATION_longitude",
            "location_field": "location",
        },
    },
    "work_orders_signs_markings": {
        "primary_key": "ATD_WORK_ORDER_ID",
        "modified_date_field": "MODIFIED_DATE",
        "modified_date_field_id": "field_2150",
        "obj": None,
        "scene": "scene_774",
        "view": "view_2226",
        "ref_obj": ["object_140", "object_11", "object_7"],
        "socrata_resource_id": "",
        "pub_log_id": "",
        "status_field": "WORK_ORDER_STATUS",
    },
}

DETETECTION_STATUS_SIGNALS = {
    "CONFIG_DETECTORS": {
        "scene": "scene_468",
        "view": "view_1333",
        "objects": ["object_98"],
    },
    "CONFIG_SIGNALS": {
        "scene": "scene_73",
        "view": "view_197",
        "objects": ["object_12"],
    },
    "CONFIG_STATUS_LOG": {"objects": ["object_102"]},
    "FIELDMAP_STATUS_LOG": {
        "EVENT": "field_1576",
        "SIGNAL": "field_1577",
        "EVENT_DATE": "field_1578",
    },
    "DET_STATUS_LABEL": "DETECTOR_STATUS",
    "DET_DATE_LABEL": "MODIFIED_DATE",
    "SIG_STATUS_LABEL": "DETECTION_STATUS",
    "SIG_DATE_LABEL": "DETECTION_STATUS_DATE",
}


LOCATION_UPDATER = {
    "filters": {
        "match": "and",
        "rules": [{"field": "field_1357", "operator": "is", "value": "No"}],
    },
    "obj": "object_11",
    "field_maps": {
        #  service name
        "EXTERNAL_cmta_stops": {
            "fields": {
                #  AGOL Field : Knack Field
                "ID": "BUS_STOPS"
            }
        }
    },
    "layers": [
        # layer config for interacting with ArcGIS Online
        # see: http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#//02r3000000p1000000
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
            "apply_format": True,
        },
    ],
}


MARKINGS_AGOL = [
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
        "ref_obj": ["object_143", "object_140", "object_141"],
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

