# Calculate # of business days elapsed and update records accordingly.

# Developed specifically for measuring Traffic Control Plan (TCP) permit
# application reviews in the Right-of-Way Management division. 

# Attributes:
#     elapsed_key (str): Description
#     end_key (str): Description
#     obj (str): Description
#     scene (str): Description
#     start_key (str): Description
#     update_fields (list): Description
#     view (str): Description

import argparse
from datetime import datetime
import os
import pdb
import traceback

import knackpy
import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import CustomBusinessDay

import _setpath
from config.secrets import *
from tdutils import argutil
from tdutils import datautil
from tdutils import emailutil
from tdutils import jobutil
from tdutils import logutil

# define config variables
scene = "scene_754"
view = "view_1987"
obj = "object_147"
start_key = "SUBMITTED_DATE"
end_key = "REVIEW_COMPLETED_DATE"
elapsed_key = "DAYS_ELAPSED"

update_fields = ["DAYS_ELAPSED", "id"]


def get_calendar():
    """Summary
    
    Returns:
        TYPE: Description
    """
    return CustomBusinessDay(calendar=USFederalHolidayCalendar())


def handle_records(data, start_key, end_key, elapsed_key, calendar):
    """Summary
    
    Args:
        data (TYPE): Description
        start_key (TYPE): Description
        end_key (TYPE): Description
        elapsed_key (TYPE): Description
        calendar (TYPE): Description
    
    Returns:
        TYPE: Description
    """
    update = []

    for record in data:
        dates = get_dates(record, start_key, end_key)

        if dates:
            elapsed = business_days_elapsed(dates["start"], dates["end"], calendar)

            try:
                old_elapsed = int(record.get(elapsed_key))

            except ValueError:
                #  assume old_elapsed is an empty string
                record[elapsed_key] = int(elapsed)
                update.append(record)
                continue

            if int(record[elapsed_key]) != int(elapsed):
                record[elapsed_key] = int(elapsed)
                update.append(record)

            else:
                continue
        else:
            continue

    return update


def get_dates(record, start_key, end_key):
    """Summary
    
    Args:
        record (TYPE): Description
        start_key (TYPE): Description
        end_key (TYPE): Description
    
    Returns:
        TYPE: Description
    """
    start = record.get(start_key)

    if start:
        start = datetime.fromtimestamp(int(start) / 1000)
    else:
        return None

    end = record.get(end_key)

    if end:
        end = datetime.fromtimestamp(int(end) / 1000)
    else:
        end = datetime.today()

    return {"start": start, "end": end}


def business_days_elapsed(start, end, calendar):
    """Summary
    
    Args:
        start (TYPE): Description
        end (TYPE): Description
        calendar (TYPE): Description
    
    Returns:
        TYPE: Description
    """
    index = pd.DatetimeIndex(start=start, end=end, freq=calendar)
    elapsed = len(index) - 1
    return elapsed


def cli_args():
    """
    Parse command-line arguments using argparse module.
    
    Returns:
        TYPE: Description
    """
    parser = argutil.get_parser(
        "tcp_business_days.py",
        "Calculate # of business days elapsed and update records accordingly.",
        "app_name",
    )

    args = parser.parse_args()

    return args


def update_record(record, obj_key, creds):
    """Summary
    
    Args:
        record (TYPE): Description
        obj_key (TYPE): Description
        creds (TYPE): Description
    
    Returns:
        TYPE: Description
    """
    res = knackpy.record(
        record,
        obj_key=obj_key,
        app_id=creds["app_id"],
        api_key=creds["api_key"],
        method="update",
    )

    return res


def main(job, **kwargs):
    """Summary
    
    Args:
        job (TYPE): Description
        **kwargs: Description
    
    Returns:
        TYPE: Description
    """
    app_name = kwargs["app_name"]

    creds = KNACK_CREDENTIALS[app_name]

    kn = knackpy.Knack(
        scene=scene,
        view=view,
        ref_obj=[obj],
        app_id=creds["app_id"],
        api_key=creds["api_key"],
    )

    calendar = get_calendar()

    kn.data = handle_records(kn.data, start_key, end_key, elapsed_key, calendar)

    # logger.info( '{} Records to Update'.format(len(kn.data) ))

    if kn.data:
        kn.data = datautil.reduce_to_keys(kn.data, update_fields)
        kn.data = datautil.replace_keys(kn.data, kn.field_map)

        for i, record in enumerate(kn.data):
            print("Update record {} of {}".format(i, len(kn.data)))
            update_record(record, obj, creds)

    return len(kn.data)

