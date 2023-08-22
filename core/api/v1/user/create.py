from core.schemas import User, ApiKey, Device
from core.utils.general import get_alphnum_id, colored_print


def retrieve_owner():
    """
    :dev This function retrieves the server owner.
    """
    user = User.query.first()
    if not user:
        return None
    else:
        return user


def create_owner():
    """
    :dev This function creates the server owner and its associated info, meta, and api key data.
    """

    # Create the user
    api_key_value = get_alphnum_id(prefix='infr_apikey_', id_len=32)
    api_key_id = get_alphnum_id(prefix='apikey_', id_len=8)
    device_id = get_alphnum_id(prefix='device_', id_len=8)
    server_owner_id = get_alphnum_id(prefix='user_', id_len=8)
    user = User(id=server_owner_id, email_id="default@temporary.com")
    user.save()

    # Add api key data
    api_key = ApiKey(id=api_key_id, name='default', description='Default API key for user',
                     key=api_key_value, access_level=['read', 'write', 'admin'])
    api_key.save()

    # Add a device
    device = Device(
        id=device_id,
        name='Personal Laptop #1',
        description='Default device for user',
        device_type='desktop'
    )
    device.save()

    return user


def create_owner_on_init():
    """
    :dev This function creates the server owner on initialization.
    """

    # Check if the user exists
    user = retrieve_owner()
    if not user:
        user = create_owner()
        colored_print('\nServer owner created successfully!', "green")
        colored_print("Owner API key: {}".format(user.to_json(include_apikeys=True)['apikeys'][0]['key']), "green")
    else:
        colored_print('\nServer owner already exists.', "blue")
    return user
