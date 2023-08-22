from flask import request, Blueprint
from flask_cors import cross_origin

from core.api.v1.segment.create import create_inference_item_from_request
from core.api.v1.segment.query import query_segments_route_wrapper, query_single_segment, query_segment_stats

segment_blueprint = Blueprint('segment_blueprint', __name__, url_prefix="/v1/segment")


@segment_blueprint.route('/create', methods=['POST'])
@cross_origin()
def create_segment_route():
    return create_inference_item_from_request(request)


@segment_blueprint.route('/query', methods=['GET'])
@cross_origin()
def query_segments_route():
    return query_segments_route_wrapper(request)


@segment_blueprint.route('/query/id/<segment_id>', methods=['GET'])
@cross_origin()
def query_single_segment_route(segment_id):
    return query_single_segment(incoming_request=request, segment_id=segment_id)


@segment_blueprint.route('/query/stats', methods=['GET'])
@cross_origin()
def query_segment_stats_route():
    return query_segment_stats(incoming_request=request)
