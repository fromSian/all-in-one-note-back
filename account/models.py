import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from utils.file import get_size, image_content_types

# Create your models here.


def validate_image_size(file):
    max_upload_size = get_size(2.5)
    if file.size > max_upload_size:
        raise ValidationError(
            _("%(value)s is larger than 2.5MB"),
            params={"value": file},
        )


def validate_image_content_type(file):
    content_types = image_content_types
    if file.content_type not in content_types:
        raise ValidationError(
            _("%(value)s is not the valid type"),
            params={"value": file.content_type},
        )


class UserManager(BaseUserManager):
    def create_user(self, email, password, **other_fields):
        user = User(email=email, **other_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save()
        return user

    def create_superuser(self, email, password, **other_fields):
        other_fields.setdefault("is_staff", True)
        other_fields.setdefault("is_superuser", True)
        other_fields.setdefault("is_active", True)

        if other_fields.get("is_staff") is not True:
            raise ValueError("Superuser must be assigned to is_staff=True")
        elif other_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must be assigned to is_superuser=True")

        return self.create_user(email, password, **other_fields)


class User(AbstractUser):
    first_name = None
    last_name = None
    username = None

    email = models.EmailField("email address", unique=True)
    password = models.CharField("password", max_length=128, blank=True)
    image = models.URLField(
        "avatar image url",
        blank=True,
    )
    TYPE_CHOICES = (
        ("base", "from_base"),
        ("google", "from_google"),
        ("trial", "from_trial"),
    )
    type = models.CharField("type", choices=TYPE_CHOICES, blank=False, default="base")

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()
