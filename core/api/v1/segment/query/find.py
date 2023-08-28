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

    # Multple device IDs, items, segements IDs and attributes can be provided as a comma separated string
    device_ids = args.get('device_ids')
    item_types = args.get('item_types')
    segment_ids = args.get('segment_ids')
    available_in = args.get('available_in')

    date_created_from = args.get('date_created_from')
    date_created_to = args.get('date_created_to')
    date_updated_from = args.get('date_updated_from')
    date_updated_to = args.get('date_updated_to')
    date_generated_from = args.get('date_generated_from')
    date_generated_to = args.get('date_generated_to')

    attributes = args.getlist('attributes')
    name = args.get('name')
    description = args.get('description')
    extracted_text = args.get('extracted_text')

    lat_tl = float(args.get('lat_tl', 0))
    lng_tl = float(args.get('lng_tl', 0))
    box_width = float(args.get('box_width', 0))

    order_by = args.get('order_by', 'date_generated')
    order_direction = args.get('order_direction', 'desc')
    limit = int(args.get('limit', 100))
    if limit > 1000:
        limit = 1000
    offset = int(args.get('offset', 0))

    vectorized_text = args.get('vectorized_text')

    include_vector = args.get('include_vector', 'false').lower() == 'true'
    include_image = args.get('include_image', 'false').lower() == 'true'
    include_bounding_box = args.get('include_bounding_box', 'false').lower() == 'true'
    include_fields = args.get('include_fields', None)

    if vectorized_text:
        vectorized_text = get_text_list_as_vectors([vectorized_text])[0]

    results = get_segments(status=status, segment_ids=segment_ids,
                           device_ids=device_ids, item_types=item_types,
                           date_created_from=date_created_from,
                           date_created_to=date_created_to, date_updated_from=date_updated_from,
                           date_updated_to=date_updated_to, date_generated_from=date_generated_from,
                           date_generated_to=date_generated_to, available_in=available_in,
                           name=name, description=description, extracted_text=extracted_text,
                           lat_tl=lat_tl, lng_tl=lng_tl, box_width=box_width, order_by=order_by,
                           order_direction=order_direction,
                           limit=limit, offset=offset, attributes=attributes,
                           vectorized_text=vectorized_text,
                           include_vector=include_vector, include_image=include_image,
                           include_bounding_box=include_bounding_box, include_fields=include_fields)

    return results


def get_segments(status=None, segment_ids=None, device_ids=None, item_types=None,
                 date_created_from=None, date_created_to=None, date_updated_from=None, date_updated_to=None,
                 date_generated_from=None, date_generated_to=None,
                 available_in=None, name=None, description=None,
                 extracted_text=None, lat_tl=None, lng_tl=None, box_width=None,
                 order_by='date_generated', order_direction='desc',
                 limit=100, offset=0, attributes=None, vectorized_text=None,
                 include_vector=False, include_image=False, include_bounding_box=False, include_fields=None):

    query = Segment.query

    # Add filters based on provided arguments
    if status:
        query = query.filter(Segment.status == status)
    if segment_ids:
        segment_id_list = segment_ids.split(',')
        query = query.filter(Segment.id.in_(segment_id_list))
    if device_ids:
        device_id_list = device_ids.split(',')
        query = query.filter(Segment.device_id.in_(device_id_list))
    if item_types:
        item_type_list = item_types.split(',')
        query = query.filter(Segment.item_type.in_(item_type_list))
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

    # Text based search items
    if name:
        query = handle_text_based_search('name', name, query)
    if description:
        query = handle_text_based_search('description', description, query)
    if extracted_text:
        query = handle_text_based_search('extracted_text', extracted_text, query)

    # Attributes filter
    if attributes:
        for attribute in attributes:
            key, value = attribute.split(':', 1)
            query = handle_text_based_search(key, value, query, is_attribute=True)

    # Geolocation bounding box filter
    if lat_tl and lng_tl and box_width:
        lat_br = lat_tl - box_width  # bottom right latitude
        lng_br = lng_tl + box_width  # bottom right longitude
        query = query.filter(and_(Segment.lat >= lat_br, Segment.lat <= lat_tl,
                             Segment.lng >= lng_tl, Segment.lng <= lng_br))

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


def handle_text_based_search(key, value, query, is_attribute=False):
    """
    :dev This function handles text based search based on the operator.
    :param key (str): Key for which search is to be performed.
    :param value (str): Value for which search is to be performed. This key may include the operator.

        - $operator:value or just value where operator is one of the following:
            - eq: Equal to
            - ilike: Case insensitive like, i.e. contains

    :param column (obj): Column object.
    :param query (obj): Query object.
    :param is_attribute (bool): Whether the key is an attribute or not.
    """

    if is_attribute:
        if "$" != value[0]:
            query = query.filter(Segment.attributes[key].astext == value)
        else:
            operator, value = value.split(':', 1)
            if operator == "$eq":
                query = query.filter(Segment.attributes[key].astext == value)
            elif operator == "$ilike":
                query = query.filter(Segment.attributes[key].astext.ilike("%"+value+"%"))

    else:
        if "$" != value[0]:
            query = query.filter(getattr(Segment, key) == value)
        else:
            operator, value = value.split(':', 1)
            if operator == "$eq":
                query = query.filter(getattr(Segment, key) == value)
            elif operator == "$ilike":
                query = query.filter(getattr(Segment, key).ilike("%"+value+"%"))

    return query
