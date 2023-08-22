from flask import Blueprint, request
from flask_cors import cross_origin

from core.api.v1.device.create import create_apikey_route_wrapper
from core.api.v1.device.update import update_device_route_wrapper
from core.api.v1.device.query import query_devices_route_wrapper

device_blueprint = Blueprint('device_blueprint', __name__, url_prefix="/v1/device")


@device_blueprint.route('/create', methods=['POST'])
@cross_origin()
def create_apikey_route():
    return create_apikey_route_wrapper(request)


@device_blueprint.route('/update', methods=['POST'])
@cross_origin()
def update_device_route():
    return update_device_route_wrapper(request)


@device_blueprint.route('/query', methods=['GET'])
@cross_origin()
def query_devices_route():
    return query_devices_route_wrapper(request)
