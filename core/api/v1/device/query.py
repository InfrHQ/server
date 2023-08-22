"""
:dev This page includes functions to query devices
"""

from core.schemas import ApiKey, Device
from core.utils.auth import verify_apikey_request
from flask import jsonify


def query_devices_route_wrapper(incoming_request):
    """
    :dev This function queries all devices in the server.
    :param incoming_request (obj): Incoming request object.
        - Headers:
            - Infr-API-Key (str): API key which should have read access.
    """

    # Verify the API key
    api_key_object, status_code = verify_apikey_request(incoming_request=incoming_request, access_level='read')
    if status_code != 200 or not isinstance(api_key_object, ApiKey):
        return api_key_object, status_code

    # Return all API keys
    devices = Device.query.all()
    return jsonify({"message": "Devices retrieved", "devices": [x.to_json() for x in devices]}), 200
