from core.schemas import Segment, ApiKey
from core.utils.auth import verify_apikey_request
from flask import jsonify


def query_single_segment(incoming_request, segment_id: str):
    """
    :dev This function queries a single segment
    :param incoming_request (obj): Incoming request object.
        - Headers:
            - Infr-API-Key (str): API key which should have read access.
    :param segment_id (str): Segment ID to query.
    :return (obj): Segment object.
    """

    # Get the API Key from the header
    api_key_obj, status = verify_apikey_request(incoming_request, 'read')
    if status != 200 or not isinstance(api_key_obj, ApiKey):
        return api_key_obj, status

    # Get the segment
    segment = Segment.query.filter(Segment.id == segment_id).first()
    if not segment:
        return jsonify({"message": "Segment not found"}), 404

    return jsonify({"message": "Segment retrieved", "segment": segment.to_json(
        include_fields=None, get_image=True, get_bouding_box=True
    )}), 200
