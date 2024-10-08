from django.core.exceptions import ValidationError
import os
from django.conf import settings
import uuid


def get_size(mb: float):
    return 1048576 * mb


image_content_types = [
    "image/jpg",
    "image/jpeg",
    "image/gif",
    "image/png",
    "image/svg+xml",
]


cotent_type_dict = {
    "jpg": "image/jpg",
    "jpeg": "image/jpeg",
    "gif": "image/gif",
    "png": "image/png",
    "svg": "image/svg+xml",
}


def handle_uploaded_file(f, name):
    file_name = uuid.uuid4().hex
    file_extension = os.path.splitext(name)[1]
    file_path = os.path.join(settings.MEDIA_URL, file_name + file_extension)
    with open(
        os.path.join(settings.MEDIA_ROOT, file_name + file_extension), "wb+"
    ) as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return file_path


from PIL import Image


def crop(file, crop_tuple):
    file_name = uuid.uuid4().hex
    file_extension = os.path.splitext(file.name)[1]
    file_path = os.path.join(settings.MEDIA_URL, file_name + file_extension)
    if not os.path.isdir(settings.MEDIA_ROOT):
        os.mkdir(settings.MEDIA_ROOT)
    with Image.open(file) as im:
        im_crop = im.crop(crop_tuple)
        im_crop.save(os.path.join(settings.MEDIA_ROOT, file_name + file_extension))
        return file_path
