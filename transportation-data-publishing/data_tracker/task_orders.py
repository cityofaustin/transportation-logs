# Scrap task orders from COA Controller webpage and upload to Data Tracker.

# Attributes:
#     CONFIG (TYPE): Description
#     KNACK_CREDS (TYPE): Description

import json
import os
import pdb
import traceback
import sys

import arrow
import knackpy
from bs4 import BeautifulSoup
import requests

import _setpath
from config.knack.config import cfg
from config.secrets import *

from tdutils import datautil
from tdutils import emailutil
from tdutils import jobutil
from tdutils import logutil

CONFIG = cfg["task_orders"]
KNACK_CREDS = KNACK_CREDENTIALS["data_tracker_prod"]


def get_html(url):
    """Summary
    
    Args:
        url (TYPE): Description
    
    Returns:
        TYPE: Description
    """
    form_data = {"DeptNumber": 2400, "Search": "Search", "TaskOrderName": ""}
    res = requests.post(url, data=form_data)
    res.raise_for_status()
    return res.text


def handle_html(html):
    """Summary
    
    Args:
        html (TYPE): Description
    
    Returns:
        TYPE: Description
    """
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.find_all("tr")

    parsed = []

    for row in rows:
        cols = row.find_all("td")
        cols = [ele.text.strip() for ele in cols]
        parsed.append(cols)

    return parsed


def handle_rows(rows, cols=["DEPT", "TASK_ORDER", "NAME", "ACTIVE"]):
    """Summary
    
    Args:
        rows (TYPE): Description
        cols (list, optional): Description
    
    Returns:
        TYPE: Description
    """
    handled = []

    for row in rows:
        #  janky check to exclude rows that don't match expected schema
        if len(row) == 4:
            handled.append(dict(zip(cols, row)))

    return handled


def compare(new_rows, existing_rows, key="TASK_ORDER"):
    """Summary
    
    Args:
        new_rows (TYPE): Description
        existing_rows (TYPE): Description
        key (str, optional): Description
    
    Returns:
        TYPE: Description
    """
    existing_ids = [str(row[key]) for row in existing_rows]
    return [row for row in new_rows if str(row[key]) not in existing_ids]


def main(job, **kwargs):
    """Summary
    
    Args:
        job (TYPE): Description
        **kwargs: Description
    
    Returns:
        TYPE: Description
    """
    html = get_html(TASK_ORDERS_ENDPOINT)
    data = handle_html(html)
    rows = handle_rows(data)

    kn = knackpy.Knack(
        scene=CONFIG["scene"],
        view=CONFIG["view"],
        ref_obj=CONFIG["ref_obj"],
        app_id=KNACK_CREDS["app_id"],
        api_key=KNACK_CREDS["api_key"],
    )

    new_rows = compare(rows, kn.data)

    new_rows = datautil.replace_keys(new_rows, kn.field_map)

    for record in new_rows:

        res = knackpy.record(
            record,
            obj_key=CONFIG["ref_obj"][0],
            app_id=KNACK_CREDS["app_id"],
            api_key=KNACK_CREDS["api_key"],
            method="create",
        )

    return len(new_rows)
