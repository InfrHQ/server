from dotenv import load_dotenv  # noqa
load_dotenv()  # noqa

import logging  # noqa
logging.basicConfig(level=logging.WARNING)  # noqa

import os

from core.api.v1.device import device_blueprint
from core.api.v1.apikey import apikey_blueprint
from core.api.v1.file import file_blueprint
from core.api.v1.segment import segment_blueprint
from core.api.v1.user import user_blueprint
from core.connectors.postgre import db
from core.configurations import Service, Postgre
from flask_migrate import Migrate
from flask_cors import CORS
from flask import Flask, send_from_directory, render_template

# Create storage/ directory if it doesn't exist
if not os.path.exists('storage'):
    os.makedirs('storage')

application = Flask(__name__)
application.config['SQLALCHEMY_DATABASE_URI'] = Postgre.uri
CORS(application)

db.init_app(application)
migrate = Migrate(application, db)

@application.route('/')
def landing_page():
    return render_template("index.html")

@application.route('/assets/<path:path>')
def send_assets(path):
    return send_from_directory("assets/", path)

@application.route('/version')
def version():
    return "1.0.0"

application.register_blueprint(user_blueprint)
application.register_blueprint(segment_blueprint)
application.register_blueprint(file_blueprint)
application.register_blueprint(apikey_blueprint)
application.register_blueprint(device_blueprint)

if __name__ == '__main__':
    debug = Service.env_type == 'dev'
    application.run(debug=debug)
    