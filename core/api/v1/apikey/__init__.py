from flask import request, Blueprint
from flask_cors import cross_origin

from core.api.v1.apikey.create import create_apikey_route_wrapper
from core.api.v1.apikey.query import query_apikey_route_wrapper, query_single_apikey_route_wrapper
from core.api.v1.apikey.update import update_apikey_route_wrapper

apikey_blueprint = Blueprint('apikey_blueprint', __name__, url_prefix="/v1/apikey")


@apikey_blueprint.route('/create', methods=['POST'])
@cross_origin()
def create_apikey_route():
    return create_apikey_route_wrapper(request)


@apikey_blueprint.route('/query', methods=['GET'])
@cross_origin()
def query_apikey_route():
    return query_apikey_route_wrapper(request)


@apikey_blueprint.route('/query/verify', methods=['GET'])
@cross_origin()
def query_single_apikey_route():
    return query_single_apikey_route_wrapper(request)


@apikey_blueprint.route('/update', methods=['POST'])
@cross_origin()
def update_apikey_route():
    return update_apikey_route_wrapper(request)
