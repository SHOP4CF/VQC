import requests
import json
import logging
from app.otherFunctions import debug_help, readConfig

"""Some predefined constants that must be known in advance"""

header = {"Content-Type": "application/ld+json"}

logger = logging.getLogger("app")


# firaware respond class
class FiwareResponse:
    final_url: str = ""
    config: dict = None
    """
    f'http://{config["fiware_host"]}:'
                               f'1026/ngsi-ld/v1/entities/urn:ngsi-ld:'
                               f'{config["entity_type"]}:'
                               f'{config["factory_id"]}:'
                               f'{config["entity_id"]}/attrs'
                               """

    def __int__(self,
                config,
                url: str):
        self.config = config
        self.final_url = url

    def set_config(self,
                   ready_config=None,
                   ) -> None:
        if type(ready_config) is str:
            self.config = readConfig.read_config(ready_config)["interface"]
        elif type(ready_config) is dict:
            self.config = ready_config

    def set_url(self,
                new_url: str) -> None:
        print(f'\n\n{self.config}\n')
        if new_url is not None:
            self.final_url = new_url
        else:
            if self.config is not None:
                print(f'\n\n\t{self.config}')
                self.final_url = f'http://{self.config["fiware_host"]}:' \
                                 f'1026/ngsi-ld/v1/entities/urn:ngsi-ld:' \
                                 f'{self.config["entity_type"]}:' \
                                 f'{self.config["factory_id"]}:' \
                                 f'{self.config["entity_id"]}/attrs'

    def respond(self,
                status: int,
                timestamp: str,
                message: str = "No errors",
                ) -> int:
        """
        Args:
            Both arguments are FIWARE attributes of our VQC entity
            status(int): status of our VQC
            timestamp(int): the timestamp of the status
            message(str): the message to pass with the response
        Returns:
            (int) the status code from the response
        """

        # ! This must reflect our FIWARE entity
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
                "https://raw.githubusercontent.com/shop4cf/"
                "data-models/master/docs/shop4cfcontext.jsonld",
            ],
        }

        update_json = json.dumps(update)
        """
        Here we send patch request that is used by FIWARE to update entity if
        we change values of some attributes then some subscription may be fired
        """
        try:
            resp = requests.patch(self.final_url, headers=header,
                                  data=update_json)
        except requests.exceptions.ConnectionError:
            msg = "app.otherFunctions.fiware_response --> Failed to connect " \
                  "with FIWARE, make sure that container is running, and " \
                  "check that all URLS are correct."
            debug_help.log_fiware_resp_exception(
                logger,
                msg,
                "error",
                send_fiware=False,
                raise_exception=True,
            )
        print(f'Updated entity {self.config["entity_id"]}: {resp.status_code}')

        # If FIWARE rejected our request we log it
        if resp.status_code != 204:
            msg = f'app.otherFunctions.Fiware_response --> Failed to update' \
                  f' entity. Make sure that Entity: ' \
                  f'{self.config["entity_id"]} exists. ' \
                  f'Error code: {resp.status_code}'
            debug_help.log_fiware_resp_exception(
                logger,
                msg,
                "error",
                send_fiware=False,
                raise_exception=True,
            )

        return resp.status_code
