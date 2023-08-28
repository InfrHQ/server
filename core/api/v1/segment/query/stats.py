from core.schemas import Segment, ApiKey
from core.utils.auth import verify_apikey_request
from flask import jsonify
from sqlalchemy import desc, asc


def query_segment_stats(incoming_request):
    """
    :dev This function queries segment stats for the server
    :param incoming_request (obj): Incoming request object.
        - Headers:
            - Infr-API-Key (str): API key which should have read access.
    """

    # Get the API Key from the header
    api_key_obj, status = verify_apikey_request(incoming_request, 'read')
    if status != 200 or not isinstance(api_key_obj, ApiKey):
        return api_key_obj, status

    # Get the following stats:
    # - Total segments
    # - First segment created
    # - Lasted segment created
    total_segments = Segment.query.count()
    first_segment = Segment.query.order_by(
        asc(Segment.date_created)).first()
    last_segment = Segment.query.order_by(
        desc(Segment.date_created)).first()

    return jsonify({
        "message": "Segment stats retrieved",
        "stats": {
            "total_segments": total_segments,
            "first_segment": first_segment.to_json(include_fields=None,
                                                   get_image=True,
                                                   get_bouding_box=False)
            if first_segment else None,
            "last_segment": last_segment.to_json(include_fields=None,
                                                 get_image=True,
                                                 get_bouding_box=False)
            if last_segment else None
        }
    }), 200
