"""
:dev This page includes functions to update API keys
"""

from core.schemas import ApiKey
from core.utils.auth import verify_apikey_request
from flask import jsonify


def update_apikey_route_wrapper(incoming_request):
    """
    :dev This function updates an API key.
    :param incoming_request (obj): Incoming request object.
        - Headers:
            - Infr-API-Key (str): API key which should have write access.
        - Body:
            - name (str): Name of the API key.
            - description (str): Description of the API key.
            - access_level (list): List of access levels. read, write, admin.
            - status (str): Status of the API key. active, inactive
            - id (str): ID of the API key.
    """

    # Verify the API key
    api_key_object, status_code = verify_apikey_request(incoming_request=incoming_request, access_level='admin')
    if status_code != 200 or not isinstance(api_key_object, ApiKey):
        return api_key_object, status_code

    # Get JSON data from the request object
    data = incoming_request.get_json()
    name = data.get('name')
    description = data.get('description')
    access_level = data.get('access_level')
    status = data.get('status')
    api_key_id = data.get('id')

    # Get the API key
    api_key = ApiKey.query.filter_by(id=api_key_id).first()
    if not api_key:
        return jsonify({"message": "API key not found"}), 404

    # Update the API key
    if name:
        api_key.name = name
    if description:
        api_key.description = description
    if access_level:
        api_key.access_level = access_level

    # If access level does not contain admin, then ensure that at least one api key with admin access level exists
    if 'admin' not in access_level:
        api_keys = ApiKey.query.all()
        admin_api_keys = [api_key for api_key in api_keys if 'admin' in api_key.access_level]
        if len(admin_api_keys) == 0:
            return jsonify({"message": "At least one API key should have admin access level"}), 400

    if status:
        api_key.status = status
    api_key.save()

    return jsonify({"message": "API key updated successfully!", "api_key": api_key.to_json()}), 200
