from django.core.exceptions import ValidationError


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
