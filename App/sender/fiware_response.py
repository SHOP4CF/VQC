"""
Here we send patch request that is used by FIWARE to update entity if we change values of 
some attributes then some subscription may be fired
"""
import json
import requests
import datetime
final_url = "http://localhost:1026/ngsi-ld/v1/entities/urn:ngsi-ld:Device:Bosch:camera1/attrs"

header = {"Content-Type": "application/json"}
id_ = "camera1"


def respond(pcb_path, template):
    # Again FIWARE need specific format of JSON, otherwise it returns error
    update = {
        "pcb_path": {"value": pcb_path, "type": "Property"},
        "value": {"value": template, "type": "Property", "observedAt": str(datetime.datetime.utcnow()).replace(" ", "T") + "Z"},
    }
    update_json = json.dumps(update)
    resp = requests.patch(final_url, headers=header, data=update_json)
    print(f"Updated entity {id_}: {resp.status_code}")
