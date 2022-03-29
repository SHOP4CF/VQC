import logging
import os

from flask import Blueprint, request

from app import Analysis
from app.otherFunctions import enums, debug_help

config = Blueprint("config", __name__, url_prefix="/config")

logger = logging.getLogger("app")


@config.route("/", methods=("GET", "POST"))
def configuration():
    """
    This method updates our Analysis object if it get POST message and when obtain GET it shows all configurations on
    the screen we could do it in more readable HTML format, or even create some HTML page in which we can update configurations.
    """
    if request.method == "GET":
        return Analysis.analysis.config
    elif request.method == "POST":
        config_path = request.data.decode(
            "utf-8"
        )  # We need to provide correct config_path
        if os.path.isfile(config_path):
            Analysis.analysis.set_config(config_path=config_path)
            msg = f"App.Config: Uploaded new config file: {config_path}"
            debug_help.log_fiware_resp_exception(
                logger, msg, send_fiware=True, fiware_status=enums.Status.Waiting
            )
            return "Config changed!"
        else:
            msg = f"App.Config: Tried to update configs with {config_path} but the file does not exits, returned code: 400"
            debug_help.log_fiware_resp_exception(
                logger,
                msg,
                level="error",
                send_fiware=True,
                fiware_status=enums.Status.Waiting,
            )
            return "Bad config Path", 400
