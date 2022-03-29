from flask import request, Response, Blueprint
import os
import json
from . import fiware_response

"""Create blueprint and some global variables to itarate over all images to be controlled"""
send = Blueprint("send", __name__, url_prefix="/send")
to_control = os.listdir("imgs/control")[
    ::-1
]  # we have predefined folder with some images
i = 0


@send.route("/", methods=["GET", "POST"])
def record():
    """Depending on type of request we do different things"""
    if request.method == "GET":
        return "Host for sending PCBS"

    """
        If we obtained POST request we assume it has correct structure and data, probably should write some ifs
    """
    data = json.loads(request.data)["data"][0]
    status = data["Status"]  # VQC may be waiting or ready for new photos
    """
        Sender will send new photo iff host is waiting
    """
    if status == "Waiting":
        global i  # Silly way to itare over paths
        fiware_response.respond(
            "../imgs/control/" +
            to_control[i], "../imgs/template/" +
            to_control[i][:2] + to_control[i][-4:]
        )
        i += 1
    elif status == "Error":
        print("Error!")
    elif status == "Busy":
        print("No Error but host is not ready yet")

    return Response(status=200)
