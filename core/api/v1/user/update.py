"""
:dev This page includes functions to update user information
"""

from core.schemas import User, ApiKey
from flask import jsonify
from core.utils.auth import verify_apikey_request


def update_user_route_wrapper(incoming_request):
    """
    :dev This function is a wrapper for the update_user_route function
    :param incoming_request: The request object
        - Headers
            - Infr-API-Key: The API key
        - JSON Body
            - name: The name of the server owner
            - description: The description of the server owner
    """

    # Get the API Key from the header
    api_key_obj, status_code = verify_apikey_request(incoming_request=incoming_request, access_level='write')
    if status_code != 200 or not isinstance(api_key_obj, ApiKey):
        return api_key_obj, status_code

    # Get args, currently only name and description are supported
    args = incoming_request.get_json()
    name = args.get('name')
    description = args.get('description')
    email_id = args.get('email_id')

    # Update the owner
    user = User.query.first()
    if name:
        user.name = name
    if description:
        user.description = description
    if email_id:
        user.email_id = email_id
    user.save()
    return jsonify({"message": "Owner updated", "user": user.to_json()}), 200
