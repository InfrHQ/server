from flask import Blueprint, make_response
from flask_cors import cross_origin
from core.connectors.storage import storage_client
from core.connectors.cache import cache_client
import json
import lzma

file_blueprint = Blueprint('file_blueprint', __name__, url_prefix="/v1/file")


@file_blueprint.route('/<file_id>', methods=['GET'])
@cross_origin()
def get_file_route(file_id):

    # Check if file exists in Redis
    # If there is a .jpg/.json at the end of the file_path, remove it
    # and get the file from the storage
    file_id = file_id.split(".")[0]
    file = cache_client.get_item(file_id)
    if file:
        data = json.loads(file)  # type: ignore
        file_path = data['file_path']
        mimetype = data['mimetype']
        file = storage_client.get_file(file_path)
        if file:
            if data['lzma_compressed']:
                file = lzma.decompress(file)
            response = make_response(file)
            response.headers.set('Content-Type', mimetype)
            return response
    else:
        return "File not found", 404
