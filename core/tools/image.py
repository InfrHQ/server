from PIL import Image
import pytesseract
from core.utils.text import clean_string
from core.connectors.storage import storage_client
import pandas as pd  # noqa
import json
import io
import lzma


def resize_image(img, fraction=0.5):
    """
    :dev This function resizes an image.
    :param img: Pillow image.
    :param fraction (float): Fraction of the original image size.
    :return img: Resized Pillow image.
    """
    # Calculate the height w.r.t to the base_width while maintaining the aspect ratio
    base_width = int(img.width * fraction)
    h_size = int(float(img.height) * fraction)
    img = img.resize((base_width, h_size))  # type: ignore
    return img


def compress_image(img, quality: int = 30):
    """
    :dev This function compresses an image.
    :param img: Pillow image.
    :param quality (int): The image quality, on a scale from 1 (worst) to 100 (best). The default is 50.
    :return img: Compressed Pillow image.
    """
    # Convert image to RGB (JPEG doesn't support alpha channel)
    # if img.mode not in ("RGB", "L"):
    #    img = img.convert("RGB")

    # Convert the image to JPEG format in memory and then back to a PIL Image
    buffer = io.BytesIO()
    img.save(buffer, "WEBP", quality=quality, optimize=True)

    # Print buffer size in bytes
    print("Size of Image after compression: {} bytes".format(len(buffer.getvalue())))
    buffer.seek(0)

    print("Size of Image after compression seek: {} bytes".format(len(buffer.getvalue())))
    img = Image.open(buffer)

    return img


def get_pillow_image_from_request(image_file):
    """
    :dev This function returns a pillow image from the incoming request.
    :param image_file (obj): Incoming request object. image_file = request.files['screenshot']
    :return image - type Image: Pillow image.
    """
    # Read the image
    image = Image.open(image_file)
    return image


def get_text_from_image(image):
    """
    :dev This function returns the text from an image.
    :param image_path (str): Path to the image.
    :return string - type str: Text from the image.
    """
    text = pytesseract.image_to_string(image)
    cleaned_text = clean_string(text)
    return cleaned_text


def get_data_from_image(image):
    """
    :dev This function returns the data from an image.
    :param image_path (str): Path to the image.
    :return string - type str: Data from the image.
    """
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DATAFRAME)
    data_json = data.to_json(orient="records")
    return json.loads(data_json)


def store_image(img, json_data, segment_id: str, item_type: str):
    """
    :dev This function stores the image and its metadata.
    :param img (str): Pillow image.
    :param json_data (dict): Data from the image.
    :param segment_id (str): Segment ID.
    :param item_type (str): Item type. screenshot, etc.
    """

    buffer = io.BytesIO()
    img.save(buffer, "WEBP", optimize=True, quality=30)
    buffer.seek(0)
    buffer_bytes = buffer.getvalue()

    # Print the size of the image
    print("Size of Image: {} bytes".format(len(buffer_bytes)))

    # Upload the image to the storage
    if item_type == "screenshot":
        storage_client.upload_file(buffer_bytes, f"segments/{segment_id}/image.webp")
        storage_client.upload_file(lzma.compress(json.dumps(json_data).encode('utf-8')),
                                   f"segments/{segment_id}/box_data.json.lzma")

    return True
