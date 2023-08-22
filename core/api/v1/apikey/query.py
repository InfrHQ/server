"""
:dev This page includes functions to query api keys
"""

from core.schemas import ApiKey
from core.utils.auth import verify_apikey_request
from flask import jsonify


def query_apikey_route_wrapper(incoming_request):
    """
    :dev This function queries API keys.
    :param incoming_request (obj): Incoming request object.
        - Headers:
            - Infr-API-Key (str): API key which should have admin access.
    """

    # Verify the API key
    api_key_object, status_code = verify_apikey_request(incoming_request=incoming_request, access_level='admin')
    if status_code != 200 or not isinstance(api_key_object, ApiKey):
        return api_key_object, status_code

    # Return all API keys
    api_keys = ApiKey.query.all()
    return jsonify({"message": "API keys retrieved", "api_keys": [x.to_json() for x in api_keys]}), 200


def query_single_apikey_route_wrapper(incoming_request):
    """
    :dev This function queries a single API key.
    :param incoming_request (obj): Incoming request object.
        - Headers:
            - Infr-API-Key (str): API key
    """

    # Verify the API key with lowest access level
    api_key_object, status_code = verify_apikey_request(incoming_request=incoming_request, access_level='read')
    if status_code != 200 or not isinstance(api_key_object, ApiKey):
        return api_key_object, status_code

    return jsonify({"message": "API key retrieved", "api_key": api_key_object.to_json()}), 200
