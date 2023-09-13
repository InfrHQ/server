"""
:dev This page includes functions to create segments
"""
import time
from flask import jsonify

from core.schemas import Segment, ApiKey, Device
from core.tools.image import (get_pillow_image_from_request, get_text_from_image,
                              get_data_from_image, store_image)
from core.tools.embedding import get_text_list_as_vectors
from core.utils.general import get_alphnum_id
from core.utils.auth import verify_apikey_request
from core.configurations import Storage
from datetime import datetime
from typing import Union, List
import base64
from io import BytesIO


def create_inference_item_from_request(incoming_request):
    """
    :dev This function creates an inference item from the incoming request
    :param incoming_request (obj): Incoming request object.
        - Headers:
            - Infr-API-Key (str): API key.
        - Args:
            - device_id (str): ID of the device of the item. desktop_app, etc.
            - type (str): Type of the item. screenshot, etc.
        - JSON:
            - json_metadata (str): JSON metadata.
            - screenshot (str->base64): Screenshot.
            - date_generated (float): Date generated. Unix timestamp.
            - lat (float): Latitude.
            - lng (float): Longitude.
    """

    # Get API Key from the header
    api_key, status_code = verify_apikey_request(incoming_request=incoming_request, access_level='write')
    if status_code != 200 or not isinstance(api_key, ApiKey):
        return api_key, status_code

    # Get source from the query params
    # Right now, we only support desktop_webapp
    device_id = incoming_request.args.get('device_id')
    if not device_id:
        return jsonify({"message": "Source not provided"}), 400
    device = Device.query.filter_by(id=device_id).first()
    if not device:
        return jsonify({"message": "Source not supported"}), 404
    if device.device_type not in ['desktop']:
        return jsonify({"message": "Source not supported"}), 400

    # Get the type from the query params
    # Right now, we only support screenshot
    item_type = incoming_request.args.get('type')
    if not item_type:
        return jsonify({"message": "Type not provided"}), 400
    if item_type not in ['screenshot']:
        return jsonify({"message": "Type not supported"}), 400

    if device.device_type == 'desktop' and item_type == 'screenshot':
        data = incoming_request.get_json()
        return handle_desktop_screenshot(device_id=device_id,
                                         image_file=data.get('screenshot'),
                                         date_generated=data.get('date_generated'),
                                         json_metadata=data.get('json_metadata'),
                                         lat=data.get('lat'), lng=data.get('lng'))
    else:
        return jsonify({"message": "Source & item not supported"}), 400


def handle_desktop_screenshot(device_id: str, image_file: Union[str, None],
                              date_generated: Union[float, None],
                              json_metadata: Union[dict, None],
                              lat: Union[float, None],
                              lng: Union[float, None]):
    """
    :dev Handle data from desktop webapp
    """

    # Get date_generated from the query params
    if not date_generated:
        return jsonify({"message": "Date generated not provided"}), 400
    date_generated = int(float(date_generated))
    if date_generated > int(time.time()):
        return jsonify({"message": "Date generated cannot be in the future"}), 400

    # Get lat, lng from the query params
    if lat:
        lat = float(lat)
    else:
        lat = None
    if lng:
        lng = float(lng)
    else:
        lng = None

    # Handle the image, if exists, convert to blob
    if not image_file or not isinstance(image_file, str):
        return jsonify({"message": "Screenshot not provided"}), 400

    # Handle json
    if not json_metadata or not isinstance(json_metadata, dict):
        return jsonify({"message": "JSON metadata not provided"}), 400

    # Handle page_html
    page_html = json_metadata.get('page_html')
    if page_html and not isinstance(page_html, str):
        return jsonify({"message": "Page HTML not provided or invalid"}), 400

    segment_id = get_alphnum_id(prefix='segment_', id_len=16)

    # Get the pillow image
    image = get_pillow_image_from_request(BytesIO(base64.b64decode(image_file)))

    # Get the bouding box & clean text data
    box_data = get_data_from_image(image)
    extracted_text = get_text_from_image(image)

    """
    Make sure the attributes JSON dict only contains the following:
    - app_name
    - window_name
    - current_url
    - bundle_id
    - bounding_box_available
    - page_html_available
    """
    attributes = {}
    for key in ['app_name', 'window_name', 'current_url', 'bundle_id']:
        if key in json_metadata:
            if isinstance(json_metadata[key], str):
                attributes[key] = json_metadata[key]
    if isinstance(box_data, list):
        attributes['bounding_box_available'] = True
    else:
        attributes['bounding_box_available'] = False
    if isinstance(page_html, str):
        attributes['page_html_available'] = True
    else:
        attributes['page_html_available'] = False

    # Get the vector
    conversion_text = extracted_text + ' ' \
        + attributes.get('window_name', '') + ' ' \
        + attributes.get('app_name', '')
    vector = get_text_list_as_vectors([conversion_text])[0]

    # Store the image & metadata
    store_image(image, box_data, page_html, segment_id, item_type='screenshot')

    # Get the name as Desktop Screenshot - Mon, 01 Jan, 2021 12:00:00 GMT - App Name - Window Name
    name = f"Desktop Screenshot - {datetime.utcfromtimestamp(date_generated).strftime('%a, %d %b, %Y %H:%M:%S GMT')}"
    if attributes.get('app_name'):
        name += f" - {attributes.get('app_name')}"
    if attributes.get('window_name'):
        name += f" - {attributes.get('window_name')}"

    # Create and store the segment
    segment = create_and_store_segment(
        segment_id=segment_id,
        date_generated=date_generated, lat=lat, lng=lng,
        vector=vector, name=name, description=None,
        extracted_text=extracted_text, attributes=attributes,
        item_type='screenshot', device_id=device_id, available_in=get_availability())

    return jsonify({"message": "Segment created successfully!", "segment": segment.to_json()}), 201


def get_availability():
    """
    :dev This function returns the availability of the storage
    """

    availability = []
    if Storage.local:
        availability.append('local')
    if Storage.third_party:
        availability.append(Storage.third_party)

    return availability


def create_and_store_segment(segment_id: str, date_generated: float, lat: Union[float, None],
                             lng: Union[float, None], vector: list, name: Union[None, str],
                             description: Union[None, str], extracted_text: str,
                             attributes: dict, item_type: str, device_id: str,
                             available_in: List[str] = ['local', 'supabase', 'azure_blob'],
                             status: str = 'active'):
    """
    :dev This function creates and stores a segment.
    :param date_generated (float): Date generated. Unix timestamp.
    :param vector (list): Vector.
    :param name (str): Name.
    :param description (str): Description.
    :param extracted_text (str): Extracted text.
    :param attributes (dict): Attributes.
    :param item_type (str): Item type.
    :param device_id (str): Device ID.
    """

    date_generated_utc = datetime.utcfromtimestamp(date_generated)

    # Create the segment
    segment = Segment(
        id=segment_id,
        lat=lat, lng=lng,
        vector=vector,
        date_generated=date_generated_utc,
        name=name,
        description=description, extracted_text=extracted_text,
        attributes=attributes, item_type=item_type, device_id=device_id,
        available_in=available_in, status=status)

    # Store the segment
    segment.save()

    return segment
