from flask import Blueprint, g, request
import json
from app import Analysis, db
from app.otherFunctions import enums, debug_help, arcvi_response
import logging

inspect = Blueprint("inspect", __name__, url_prefix="/inspect")

logger = logging.getLogger("app")

outcomes = []


@inspect.after_request
def check(response):
    """
    Now this method will always be fired when we do request to that particular blueprint - namely inspect. So we need to
    write some exceptions when we got different kind of request.
    When we obtain GET here we do nothing, but maybe write some if reacting when we got POST but with some wrong data
    """
    if request.method == "GET":
        print("GET Request received")
        return response
    else:
        print("POST Request received")
        
    """In case during our POST we do not obtain path and template we return response"""
    if "pcb_path" not in g or "template" not in g:
        logger.error(
            "App.Inspect: Couldn't find pcb_path and/or template in Flask's g object"
        )
        response.status_code = 400
        return response
    """
        Path and template are stored inside global g variable that is available within one request.
    """
    pcb_path = g.pcb_path
    template = g.template
    print(
        f"Will be checking PCB_PATH: {pcb_path}  TEMPLATE: {template}", flush=True)

    """We use response call_one_close so that at first we send the response and then we apply our function it is done
    to prevent timeouts"""

    @response.call_on_close
    def callback():
        """Getting path for tamplate from database we using db.py file for that"""
        if Analysis.analysis.config["interface"]["use_db"]:
            template_url = db.mongo_db.get_template(template)
        else:
            template_url = template

        """ Checking current PCB and printing result"""
        
        result, path_to_visualization = Analysis.analysis.analyse(
            template, pcb_path
        )
        """
        After we carried inspection we update our entity inside FIWARE after that sender will obtain notification
        and based on what we've sent he will update itself   
        """
        msg = f"Checked: {pcb_path}, using template: {template_url}, result: {result}. Results saved in: {path_to_visualization}"
        arcvi_response.respond(path_to_visualization, result) # Sending results to ARCVI component
        fiware_status_code = debug_help.log_fiware_resp_exception(
            logger, msg, send_fiware=True, fiware_status=enums.Status.Waiting
        )

        # We store one last outcome globally, it is very usefull while testing, and I think having array of length 1 is
        # okay, as it does not take a lot of memory.
        global outcomes
        outcomes = [
            json.dumps(
                {
                    "template": template,
                    "pcb": pcb_path,
                    "method": Analysis.analysis.get_method(),
                    "result": result,
                    "fiware_response": fiware_status_code,
                }
            )
        ]

    return response


@inspect.route("/", methods=("GET", "POST"))
def analyse():
    """
    The deal is that we have to return some string from that function, because when I tried to return Response object
    then callback was executed before sending response when I substituted it with string It works as it should.
    Basically flask by default returns response object even if we don't do it explicitly so I don't know why this worked
    that way
    """
    if request.method == "GET":
        return str(outcomes)
    elif request.method == "POST":
        try:
            data = json.loads(request.data)["data"][0]
        except json.decoder.JSONDecodeError:
            msg = "app.Inspect: Got POST with data that could not be decoded into JSON. This may be due some bad FIWARE settings or some wrong POST content"
            debug_help.log_fiware_resp_exception(
                logger,
                msg,
                level="error",
                send_fiware=True,
                fiware_status=enums.Status.Error,
            )
            return "Invalid post message"

        try:
            # ! We seek for the attribute that is given in config
            g.pcb_path = data[Analysis.analysis.config["interface"]
                              ["to_inspect_attr"]]
            g.template = data[Analysis.analysis.config["interface"]
                              ["template_attr"]]
        except KeyError:
            msg = f'App.inspect: Not able to find needed values in data dict. It may be due some FIWARE settings or wrong POST content'
            debug_help.log_fiware_resp_exception(
                logger,
                msg,
                level="error",
                send_fiware=True,
                fiware_status=enums.Status.Error,
                raise_exception=True,
            )

    return "Thanks"
