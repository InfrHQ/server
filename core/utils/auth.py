from core.schemas import ApiKey
from typing import Union, Tuple


def verify_apikey_request(incoming_request, access_level: str) -> Union[Tuple[dict, int], Tuple[ApiKey, int]]:
    """
    :dev This function verifies that the incoming request is from an API key.
    """

    # Get the Infr-API-Key header
    api_key = incoming_request.headers.get('Infr-API-Key')
    if not api_key:
        return {"message": "API key not provided"}, 401

    # Verify the API key
    api_key_object = ApiKey.query.filter_by(key=api_key).first()
    if not api_key_object:
        return {"message": "API key not found"}, 401
    if api_key_object.status != 'active':
        return {"message": "API key not active"}, 401

    # Verify the access level
    if access_level not in api_key_object.access_level:
        return {"message": "API key does not have access"}, 401

    return api_key_object, 200
