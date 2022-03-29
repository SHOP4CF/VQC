import requests
import json
import logging
import os
import yaml
from app.otherFunctions import debug_help

"""Some predefined constants that must be known in advance"""

with open(os.path.join("configuration", "configuration.yaml"), "r") as f:
    configuration = yaml.safe_load(f)

#! We get all information to build proper URL
fiware_host = configuration["interface"]["fiware_host"]
entity_type = configuration["interface"]["entity_type"]
factory_id = configuration["interface"]["factory_id"]
entity_id = configuration["interface"]["entity_id"]

final_url = f"http://{fiware_host}:1026/ngsi-ld/v1/entities/urn:ngsi-ld:{entity_type}:{factory_id}:{entity_id}/attrs"
header = {"Content-Type": "application/ld+json"}

logger = logging.getLogger("app")


def respond(status, timestamp, message="No errors"):
    """
    Args:
        Both arguments are FIWARE attributes of our VQC entity
        status(int): status of our VQC
        control_sum(int): control sum is needed so that always some attribute is updated
    """

    #! This must reflect our FIWARE entity
    update = {
        "Status": {
            "value": status,
            "type": "Property",
            "observedAt": timestamp.replace(" ", "T") + "Z",
        },
        "workParameters": {
            "type": "Property",
            "value": {"message": message, "controlled": []},
        },
        "@context": [
            "https://smartdatamodels.org/context.jsonld",
            "https://raw.githubusercontent.com/shop4cf/data-models/master/docs/shop4cfcontext.jsonld",
        ],
    }
    update_json = json.dumps(update)
    """
    Here we send patch request that is used by FIWARE to update entity if we change values of
    some attributes then some subscription may be fired
    """
    try:
        resp = requests.patch(final_url, headers=header, data=update_json)
    except requests.exceptions.ConnectionError:
        msg = f"app.otherFunctions.fiware_response --> Failed to connect with FIWARE, make sure that container is running, and check that all URLS are correct."
        debug_help.log_fiware_resp_exception(
            logger,
            msg,
            "error",
            send_fiware=False,
            raise_exception=True,
        )
    print(f"Updated entity {entity_id}: {resp.status_code}")

    # If FIWARE rejected our request we log it
    if resp.status_code != 204:
        msg = f"app.otherFunctions.Fiware_response --> Failed to update entity. Make sure that Entity: {entity_id} exists. Error code: {resp.status_code}"
        debug_help.log_fiware_resp_exception(
            logger,
            msg,
            "error",
            send_fiware=False,
            raise_exception=True,
        )

    return resp.status_code
