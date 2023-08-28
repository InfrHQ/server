from core.schemas import Segment, ApiKey
from core.utils.auth import verify_apikey_request
from flask import jsonify


def query_unique_route_wrapper(incoming_request):
    """
    :dev This function queries unique values for the given keys.
    :param incoming_request (obj): Incoming request object.
        - Headers:
            - Infr-API-Key (str): API key which should have read access.
        - Args:
            - keys (list of str): List of keys for which unique values are to be fetched.
    """

    # Get the API Key from the header
    api_key_obj, status = verify_apikey_request(incoming_request, 'read')
    if status != 200 or not isinstance(api_key_obj, ApiKey):
        return api_key_obj, status

    # Get the keys for which unique values are to be fetched
    keys = incoming_request.args.get('keys')
    if not keys:
        return jsonify({"message": "No keys provided"}), 400
    keys = keys.split(',')

    # Get the unique values for the provided keys
    unique_values = get_unique_values(keys)

    return jsonify({"message": "Unique values retrieved", "unique_values": unique_values}), 200


def get_unique_values(keys: list):
    """
    :dev Fetch unique values for the given keys.
    """
    unique_values = {}

    for key in keys:
        # If it's a regular attribute of Segment model and not an attribute key
        if hasattr(Segment, key) and not key.startswith('attributes.'):
            values = (Segment.query.with_entities(getattr(Segment, key))
                      .distinct()
                      .limit(100)
                      .all())
            unique_values[key] = [value[0] for value in values if value[0]]

        # If it's inside the JSONB attributes
        elif key.startswith('attributes.'):
            attribute_key = key.split('attributes.', 1)[-1]
            values = (Segment.query.with_entities(Segment.attributes[attribute_key].astext)
                      .distinct()
                      .limit(100)
                      .all())
            unique_values[key] = [value[0] for value in values if value[0]]

    return unique_values
