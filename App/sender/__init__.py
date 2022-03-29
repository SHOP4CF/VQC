from flask import Flask
import yaml

"""
This is a dummy implementation of camera we tried to anyhow simulate its behaviour
"""
def create_app():
    app = Flask(__name__, instance_relative_config=True)

    from . import send
    app.register_blueprint(send.send)

    return app
