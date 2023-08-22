from core.schemas import User, ApiKey
from core.utils.auth import verify_apikey_request


def retrieve_user_by_apikey_route_wrapper(incoming_request):
    """
    :dev This function retrieves the server owner.
    """

    # Verfiy service
    apikey, status = verify_apikey_request(incoming_request, 'read')
    if status != 200 or not isinstance(apikey, ApiKey):
        return apikey, status

    user = User.query.first()

    # Only include api keys if api key is admin
    include_apikeys = True if 'admin' in apikey.access_level else False
    if not user:
        return {"message": "User not found"}, 404
    else:
        return {"message": "User found", "user": user.to_json(include_apikeys=include_apikeys)}, 200
