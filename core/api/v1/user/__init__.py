from flask import request, Blueprint
from flask_cors import cross_origin

from core.api.v1.user.query import retrieve_user_by_apikey_route_wrapper
from core.api.v1.user.update import update_user_route_wrapper
from core.api.v1.user.create import create_owner_on_init

user_blueprint = Blueprint('user_blueprint', __name__, url_prefix="/v1/user")


@user_blueprint.route('/query/apikey', methods=['GET'])
@cross_origin()
def retrieve_user_by_apikey_route():
    return retrieve_user_by_apikey_route_wrapper(request)


@user_blueprint.route('/update', methods=['POST'])
@cross_origin()
def update_user_route():
    return update_user_route_wrapper(request)


@user_blueprint.cli.command('create-owner')
def create_owner():
    create_owner_on_init()
