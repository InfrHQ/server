from core.connectors.iql import IQL
from core.utils.auth import verify_apikey_request
from core.schemas import ApiKey
from flask import jsonify

import base64


def query_iql_wrapper(incoming_request):
    """
    :dev This function queries segments
    :param incoming_request (obj): Incoming request object.
        - Headers:
            - Infr-API-Key (str): API key which should have read access.
        - Args:
            - query (str): IQL query.
    """

    # Get the API Key from the header
    api_key_obj, status = verify_apikey_request(incoming_request, 'read')
    if status != 200 or not isinstance(api_key_obj, ApiKey):
        return api_key_obj, status

    # Get args
    query = incoming_request.args.get('query')
    query_text = base64.b64decode(query).decode('utf-8')

    # Query IQL
    iql = IQL(query_text)
    iql.parse()
    values = iql.handle(None)

    # Return
    return jsonify(values), 200
