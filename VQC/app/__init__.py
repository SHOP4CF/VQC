import os
from flask import Flask
import yaml

from app.otherFunctions import create_logger, readConfig


"""In here we create all loggers that can be used inside app"""
if not os.path.isdir("logs"):
    os.mkdir("logs")

create_logger.create_loggers(["db", "app"], ["logs/db.log", "logs/app.log"])


def create_app(test_config=os.path.join("config", "configuration.yaml")):
    """
    Args:
        test_config (dict): dictonary with additional configurations for test
        if needed
    Returns:
        app (Flask object): app that will be runned by our server
    """
    app = Flask(__name__, instance_relative_config=True)

    with open(test_config) as f:
        app.config["DB"] = yaml.safe_load(f)

    """Initializing our main component."""
    vqc_config = readConfig.read_config(
        test_config)
    from app import Analysis

    Analysis.analysis = Analysis.Analysis(vqc_config)

    """While testing we pass some special configs"""
    """
    if test_config:
        print(f"\n\ntest_config:\t{test_config}\n\n")
        print(f"\n\napp.config:\t{app.config}\n\n")
        app.config.from_mapping(test_config)
"""
    """If user want to connect with db we try to do it"""
    if vqc_config["interface"]["use_db"]:
        """
        If there is possibility we try to connect with the db
        """
        from app import db
        db.mongo_db.connect_db(app)

    """
    Importing and registering our two blueprint one is responsible for carrying
    out inspection and second is
    for setting configs
    """
    from app import inspect

    app.register_blueprint(inspect.inspect)

    from app import config

    app.register_blueprint(config.config)

    return app
