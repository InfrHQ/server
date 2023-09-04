"""
:dev The following are general util functions
"""
import random
import string
from core.configurations import Service
from typing import Literal


def get_alphnum_id(prefix: str, id_len: int) -> str:
    _id = (prefix+''.join(random.choices(string.ascii_letters + string.digits, k=id_len))).lower()
    return _id


def verify_admin_request(incoming_request):
    """
    :dev This function verifies that the incoming request is from an admin.
    """

    # Get the Infr-Admin-Secret header
    admin_secret = incoming_request.headers.get('Infr-Admin-Secret')
    if not admin_secret:
        return False

    # Verify the admin secret
    if admin_secret != Service.admin_secret:
        return False

    return True


def colored_print(text, color: Literal["red", "green", "yellow", "blue", "white", "reset"] = "reset"):
    """
    :dev This function prints colored text to the console.
    :param text (str): Text.
    :param color (str): Color.
    """
    color_codes = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "white": "none",
        "reset": "\033[0m"
    }
    if color_codes[color] == "none":
        print(text)
    else:
        print(color_codes[color] + text + color_codes["reset"])

    return None
