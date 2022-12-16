import requests
import json
import logging
import time
import os
import app.otherFunctions.debug_help as dh

# ensure that the responder config is available
if dh.fiware_responder is None:
    dh.init_fiware_responder(os.path.join("config", "configuration.yaml"))

url = f'http://{dh.fiware_responder.config["fiware_host"]}:' \
      f'1026/ngsi-ld/v1/entities'
headers = {
    "Content-Type": "application/ld+json",
}
logger = logging.getLogger("app")

update = {
    # ! This must be filled depending on the company name and the task number
    "id": "",
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
                    "name": "",  # ! This must be filled
                    "type": "1",  # ! This must be filled
                    "id": "0",
                }
            ],
            # #! I don't even know what this does
            "pois": [
                {
                    "position": ["0.4", "-0.15", "0.0"],
                    "radius": "0.001",
                    "label": "Defected",
                    "fill_color": {"r": "0.7", "g": "0.7", "b": "0.7",
                                   "a": "0.7"},
                    "border_color": {"r": "1.0", "g": "1.0", "b": "1.0",
                                     "a": "1.0"},
                },
            ],
        },
    },
    "@context": [
        "https://smartdatamodels.org/context.jsonld",
        "https://raw.githubusercontent.com/shop4cf/"
        "data-models/master/docs/shop4cfcontext.jsonld",
    ],
}


def respond(
        pcb_path: str = os.path.join("outcome", "outcome1.png"),
        result: str = "1",
        company: str = "Bosch"
) -> None:
    print("Response...")
    json_data = generate_data(pcb_path, result, company)
    # print(type(update))
    update_json = json.dumps(json_data)
    # print(update_json)
    response = requests.post(dh.fiware_responder.final_url, headers=headers, data=update_json)
    print("Response to ARCVI at: ", url, response.status_code)
    print(response.text)


def generate_data(
        pcb_path: str = "outcome/outcome1.png",
        result: str = "1",
        company: str = "Bosch"
):
    task = str(time.time())
    update["id"] = f"urn:ngsi-ld:Task:{company}:{task}"
    update["workParameters"]["value"]["images"][0]["path"] = pcb_path
    update["workParameters"]["value"]["outcomes"][0]["name"] = result

    return update
