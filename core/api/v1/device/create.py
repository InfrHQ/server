"""
:dev This page includes functions to create devices
"""

from core.schemas import Device, ApiKey
from core.utils.general import get_alphnum_id
from core.utils.auth import verify_apikey_request
from flask import jsonify


def create_apikey_route_wrapper(incoming_request):
    """
    :dev This function creates a Device
    :param incoming_request (obj): Incoming request object.
        - Headers:
            - Infr-API-Key (str): API key which should have write access.
        - Body:
            - name (str): Name of the Device.
            - description (str): Description of the device.
            - device_type (str): Type of the device.
    """

    # Get the API Key from the header
    api_key_object, status_code = verify_apikey_request(incoming_request=incoming_request, access_level='admin')
    if status_code != 200 or not isinstance(api_key_object, ApiKey):
        return jsonify({"message": "API key not found"}), status_code

    # Get JSON data from the request object
    data = incoming_request.get_json()
    name = data.get('name')
    description = data.get('description')
    device_type = data.get('device_type')
    if not name or not description or not device_type:
        return jsonify({"message": "Invalid data provided"}), 400
    if device_type not in ['mobile', 'desktop', 'tablet']:
        return jsonify({"message": "Invalid device type provided"}), 400

    # Create the device
    device_id = get_alphnum_id(prefix='device_', id_len=8)
    device = Device(
        id=device_id,
        name=name,
        description=description,
        device_type=device_type
    )
    device.save()

    return jsonify({"message": "Device created successfully!", "device": device.to_json()}), 201
