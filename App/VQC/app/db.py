from flask_pymongo import PyMongo
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError
import logging
from app.otherFunctions import enums, debug_help

logger = logging.getLogger("db")
"""
I keep the DB object global as it seems that they have done similar thing in documentation. Only db.py uses that object.
and basically after connection is established we do not modify this class so I believe it is quite save to have it as global
"""


class DB_connector:
    def __init__(self):
        """We create two variables that we will initialize during connection"""
        self.connection = None
        self.collection_name = None

    def connect_db(self, app):
        """
        In here we just connect to the database using some configs having host_name, passwords etc. and just
        update our mongo instance
        """
        config = app.config["DB"]
        app.config[
            "MONGO_URI"
        ] = f'mongodb://{config["host_name"]}:{config["port"]}/{config["db"]}'

        # This piece of code always works something may go wrong if we passed bad authentications as soon as we want to send a request to db
        self.collection_name = config["collection_name"]

        try:
            self.connection = PyMongo(app)
            if (
                self.connection == None
                or self.collection_name
                not in self.connection.db.list_collection_names()
            ):
                msg = (
                    f"App.db: There is no {self.collection_name} collection in the db!"
                )
                debug_help.log_fiware_resp_exception(
                    logger,
                    msg,
                    level="error",
                    send_fiware=True,
                    fiware_status=enums.Status.Error,
                    raise_exception=True,
                )

        except (OperationFailure, ServerSelectionTimeoutError):
            msg = "App.db: Could not establish connection with Database! Make sure URL and authentication data is proper"
            debug_help.log_fiware_resp_exception(
                logger,
                msg,
                level="error",
                send_fiware=True,
                fiware_status=enums.Status.Error,
                raise_exception=True,
            )

    def get_template(self, template_id):
        """We only need to return one Document from Mongo"""
        return self.connection.db[self.collection_name].find_one(
            {"template_id": template_id}
        )["template_path"]

    def get_all_templates(self):
        # Added function that returns all templates but not testing one which has id equal to 0
        return [
            {"id": x["template_id"], "template_path": x["template_path"]}
            for x in self.connection.db[self.collection_name].find(
                {"template_id": {"$gt": 0}}
            )
        ]


mongo_db = DB_connector()
