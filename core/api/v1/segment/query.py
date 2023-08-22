"""
:dev This page includes functions to query segments
"""

from core.schemas import Segment, ApiKey
from core.tools.embedding import get_text_list_as_vectors
from flask import jsonify
from sqlalchemy import and_, desc, asc
from concurrent.futures import ThreadPoolExecutor
from core.utils.auth import verify_apikey_request
from datetime import datetime


def query_segments_route_wrapper(incoming_request):
    """
    :dev This function queries segments
    :param incoming_request (obj): Incoming request object.
        - Headers:
            - Infr-API-Key (str): API key which should have read access.
        - Args:
            - see query below
    """

    # Get the API Key from the header
    api_key_obj, status = verify_apikey_request(incoming_request, 'read')
    if status != 200 or not isinstance(api_key_obj, ApiKey):
        return api_key_obj, status

    # Get args
    args = incoming_request.args

    # Get the segments
    results = get_segment_arg_wrapper(args)

    return jsonify({"message": "Segments retrieved", "segments": results}), 200


def get_segment_arg_wrapper(args):
    """
    :dev This is a wrapper function to get the segment ID from the request args.
    """
    status = args.get('status')
    device_id = args.get('device_id')
    item_type = args.get('item_type')

    date_created_from = args.get('date_created_from')
    date_created_to = args.get('date_created_to')
    date_updated_from = args.get('date_updated_from')
    date_updated_to = args.get('date_updated_to')
    date_generated_from = args.get('date_generated_from')
    date_generated_to = args.get('date_generated_to')

    available_in = args.get('available_in')
    name_contains = args.get('name_contains')
    description_contains = args.get('description_contains')
    extracted_text_contains = args.get('extracted_text_contains')
    lat_tl = float(args.get('lat_tl', 0))
    lng_tl = float(args.get('lng_tl', 0))
    box_width = float(args.get('box_width', 0))
    order_by = args.get('order_by', 'date_created')
    order_direction = args.get('order_direction', 'desc')
    limit = int(args.get('limit', 100))
    if limit > 100:
        limit = 100
    offset = int(args.get('offset', 0))
    attributes = args.get('attributes')
    vectorized_text = args.get('vectorized_text')

    include_vector = args.get('include_vector', 'false').lower() == 'true'
    include_image = args.get('include_image', 'false').lower() == 'true'
    include_bounding_box = args.get('include_bounding_box', 'false').lower() == 'true'
    include_fields = args.get('include_fields', None)

    if vectorized_text:
        vectorized_text = get_text_list_as_vectors([vectorized_text])[0]

    results = get_segments(status=status, device_id=device_id, item_type=item_type, date_created_from=date_created_from,
                           date_created_to=date_created_to, date_updated_from=date_updated_from,
                           date_updated_to=date_updated_to, date_generated_from=date_generated_from,
                           date_generated_to=date_generated_to, available_in=available_in,
                           name_contains=name_contains, description_contains=description_contains,
                           extracted_text_contains=extracted_text_contains, lat_tl=lat_tl, lng_tl=lng_tl,
                           box_width=box_width, order_by=order_by, order_direction=order_direction,
                           limit=limit, offset=offset, attributes=attributes,
                           vectorized_text=vectorized_text,
                           include_vector=include_vector, include_image=include_image,
                           include_bounding_box=include_bounding_box, include_fields=include_fields)

    return results


def get_segments(status=None, device_id=None, item_type=None, date_created_from=None,
                 date_created_to=None, date_updated_from=None, date_updated_to=None,
                 date_generated_from=None, date_generated_to=None,
                 available_in=None, name_contains=None, description_contains=None,
                 extracted_text_contains=None, lat_tl=None, lng_tl=None, box_width=None,
                 order_by='date_created', order_direction='desc',
                 limit=100, offset=0, attributes=None, vectorized_text=None,
                 include_vector=False, include_image=False, include_bounding_box=False, include_fields=None):

    query = Segment.query

    # Add filters based on provided arguments
    if status:
        query = query.filter(Segment.status == status)
    if device_id:
        query = query.filter(Segment.device_id == device_id)
    if item_type:
        query = query.filter(Segment.item_type == item_type)
    if date_created_from and date_created_to:
        date_created_from, date_created_to = datetime.fromtimestamp(
            date_created_from), datetime.fromtimestamp(date_created_to)
        query = query.filter(and_(Segment.date_created >= date_created_from, Segment.date_created <= date_created_to))
    if date_updated_from and date_updated_to:
        date_updated_from, date_updated_to = datetime.fromtimestamp(
            date_updated_from), datetime.fromtimestamp(date_updated_to)
        query = query.filter(and_(Segment.date_updated >= date_updated_from, Segment.date_updated <= date_updated_to))
    if date_generated_from and date_generated_to:
        date_generated_from, date_generated_to = datetime.fromtimestamp(
            date_generated_from), datetime.fromtimestamp(date_generated_to)
        query = query.filter(and_(Segment.date_generated >= date_generated_from,
                             Segment.date_generated <= date_generated_to))
    if available_in:
        query = query.filter(Segment.available_in.contains(available_in))
    if name_contains:
        query = query.filter(Segment.name.contains(name_contains))
    if description_contains:
        query = query.filter(Segment.description.contains(description_contains))
    if extracted_text_contains:
        query = query.filter(Segment.extracted_text.contains(extracted_text_contains))

    # Geolocation bounding box filter
    if lat_tl and lng_tl and box_width:
        lat_br = lat_tl - box_width  # bottom right latitude
        lng_br = lng_tl + box_width  # bottom right longitude
        query = query.filter(and_(Segment.lat >= lat_br, Segment.lat <= lat_tl,
                             Segment.lng >= lng_tl, Segment.lng <= lng_br))

    # Attributes filter
    if attributes:
        key, value = attributes.split(':')
        query = query.filter(Segment.attributes[key].astext == value)

    # Vectorized text search using pgvector
    if vectorized_text:
        # Assuming you have set up an index on the `vector` column with pgvector
        query = query.order_by(Segment.vector.l2_distance(vectorized_text))

    # Order the query
    elif order_direction == 'desc':
        query = query.order_by(desc(getattr(Segment, order_by)))
    else:
        query = query.order_by(asc(getattr(Segment, order_by)))

    # Limit and offset for pagination
    query = query.limit(limit).offset(offset)

    def fetch_json(segment):
        return segment.to_json(include_fields=include_fields,
                               get_vector=include_vector,
                               get_image=include_image,
                               get_bouding_box=include_bounding_box)

    segments = query.all()
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(fetch_json, segments))

    return results


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
