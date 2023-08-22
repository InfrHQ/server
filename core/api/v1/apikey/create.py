"""
:dev This page includes functions to create API keys
"""

from core.schemas import ApiKey
from core.utils.general import get_alphnum_id
from core.utils.auth import verify_apikey_request
from flask import jsonify


def create_apikey_route_wrapper(incoming_request):
    """
    :dev This function creates an API key
    :param incoming_request (obj): Incoming request object.
        - Headers:
            - Infr-API-Key (str): API key which should have write access.
        - Body:
            - name (str): Name of the API key.
            - description (str): Description of the API key.
            - access_level (list): List of access levels. read, write, admin.
    """

    # Get the API Key from the header
    api_key_object, status_code = verify_apikey_request(incoming_request=incoming_request, access_level='admin')
    if status_code != 200 or not isinstance(api_key_object, ApiKey):
        return jsonify({"message": "API key not found"}), status_code

    # Get JSON data from the request object
    data = incoming_request.get_json()
    name = data.get('name')
    description = data.get('description')
    access_level = data.get('access_level')
    if not name or not description or not access_level:
        return jsonify({"message": "Invalid data provided"}), 400
    if not isinstance(access_level, list):
        return jsonify({"message": "Invalid access_level provided"}), 400
    if not all([x in ['read', 'write'] for x in access_level]):
        return jsonify({"message": "Invalid access_level provided"}), 400

    # Create the API key
    api_key_value = get_alphnum_id(prefix='infr_apikey_', id_len=32)
    api_key_id = get_alphnum_id(prefix='apikey_', id_len=8)

    api_key = ApiKey(id=api_key_id,
                     name=name,
                     description=description, key=api_key_value,
                     access_level=access_level)
    api_key.save()

    return jsonify({"message": "API key created successfully!", "api_key": api_key.to_json()}), 201
