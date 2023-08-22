"""
:dev This page includes functions to update a device
"""

from core.schemas import ApiKey, Device
from core.utils.auth import verify_apikey_request
from flask import jsonify


def update_device_route_wrapper(incoming_request):
    """
    :dev This function updates a Device.
    :param incoming_request (obj): Incoming request object.
        - Headers:
            - Infr-API-Key (str): API key which should have write access.
        - Body:
            - name (str): Name of the device.
            - description (str): Description of the device.
            - status (str): Status of the Device. active, inactive
            - id (str): ID of the Device
    """

    # Verify the API key
    api_key_object, status_code = verify_apikey_request(incoming_request=incoming_request, access_level='write')
    if status_code != 200 or not isinstance(api_key_object, ApiKey):
        return api_key_object, status_code

    # Get JSON data from the request object
    data = incoming_request.get_json()
    name = data.get('name')
    description = data.get('description')
    status = data.get('status')
    device_id = data.get('id')

    # Get the Device
    device = Device.query.filter_by(id=device_id).first()
    if not device:
        return jsonify({"message": "Device not found"}), 404

    # Update the Device
    if name:
        device.name = name
    if description:
        device.description = description
    if status:
        device.status = status
    device.save()

    return jsonify({"message": "Device updated successfully!", "device": device.to_json()}), 200
