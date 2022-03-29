import requests
import json
import logging
import time
from app.otherFunctions import enums, debug_help

url = "http://host.docker.internal:1026/ngsi-ld/v1/entities"
headers = {
    "Content-Type": "application/ld+json",
}
logger = logging.getLogger("app")

update = {
    "id": "",  # ! This must be filled depending on the company name and the task number
    "type": "Task",
    "workParameters": {
        "type": "Property",
        "value": {
            "type": "Add",
            "images": [
                {
                    "position": ["-0.45", "0.25", "0.0"],
                    "width": "750.0",
                    "height": "1000.0",
                    "path": "/outcomes/outcome1.png",  # !This must be filled
                }
            ],
            "outcomes": [
                {
                    "name": "",  #! This must be filled
                    "type": "1",  #! This must be filled
                    "id": "0",
                }
            ],
            # #! I don't even know what this does
            "pois": [
                {
                    "position": ["0.4", "-0.15", "0.0"],
                    "radius": "0.001",
                    "label": "Defected",
                    "fill_color": {"r": "0.7", "g": "0.7", "b": "0.7", "a": "0.7"},
                    "border_color": {"r": "1.0", "g": "1.0", "b": "1.0", "a": "1.0"},
                },
            ],
        },
    },
    "@context": [
        "https://smartdatamodels.org/context.jsonld",
        "https://raw.githubusercontent.com/shop4cf/data-models/master/docs/shop4cfcontext.jsonld",
    ],
}


def respond(
    pcb_path="outcome/outcome1.png",
    result="1",
    company="Bosch",
):
    task = str(time.time())
    print("Response...")
    update["id"] = f"urn:ngsi-ld:Task:{company}:{task}"
    update["workParameters"]["value"]["images"][0]["path"] = pcb_path
    update["workParameters"]["value"]["outcomes"][0]["name"] = result
    # print(type(update))
    update_json = json.dumps(update)
    # print(update_json)
    response = requests.post(url, headers=headers, data=update_json)
    print("Response to ARCVI at: ", url, response.status_code)
    print(response.text)
