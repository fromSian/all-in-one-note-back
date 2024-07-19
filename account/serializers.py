from rest_framework import serializers
from utils.serializers import EncryptSerializerMixin
from utils.encryption import RSAEncryption
from .models import User, Settings
from django.contrib.auth.models import Group
from rest_framework.serializers import ImageField
from utils.file import get_size, image_content_types, handle_uploaded_file
from rest_framework.exceptions import ValidationError


class SettingsSerializer(EncryptSerializerMixin, serializers.ModelSerializer):

    class Meta:
        model = Settings
        exclude = ("user", "id")
        encryption_class = RSAEncryption


class UserSerializer(EncryptSerializerMixin, serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["email", "password", "image", "type", "id"]
        encryption_class = RSAEncryption
        # encrypt_fields = ("password",)
        # read_only_fields = ("type",)
        # write_only_fields = ("password",)
        extra_kwargs = {
            "password": {
                "write_only": True,
                "required": False,
            },
        }

    def create(self, validated_data):
        normal = Group.objects.filter(name="front").first()
        if not normal:
            normal = Group.objects.create(name="front")
        user = User.objects.create_user(**validated_data)
        user.groups.add(normal)
        return user

    def update(self, instance, validated_data):
        print(validated_data)
        for key, value in validated_data.items():
            if key == "password":
                instance.set_password(value)
            else:
                setattr(instance, key, value)
        instance.save()
        return instance


def validate_image_size(file):
    max_mb = 10
    max_upload_size = get_size(10)
    if file.size > max_upload_size:
        raise ValidationError(
            _("%(value)s is larger than %(size)sMB"),
            params={"value": file, "size": max_mb},
        )


def validate_image_content_type(file):
    content_types = [
        "image/jpg",
        "image/jpeg",
        "image/gif",
        "image/png",
        "image/svg+xml",
    ]
    if file.content_type not in content_types:
        raise ValidationError(
            _("%(value)s is not the valid type"),
            params={"value": file.content_type},
        )


class ImageFileSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        validate_image_content_type(value)
        validate_image_size(value)
        return value
