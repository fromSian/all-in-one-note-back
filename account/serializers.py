from rest_framework import serializers
from utils.serializers import EncryptSerializerMixin
from utils.encryption import RSAEncryption
from .models import User
from django.contrib.auth.models import Group
from rest_framework.serializers import ImageField

class UserSerializer(EncryptSerializerMixin, serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["email", "password", "avatar", "bio"]
        encryption_class = RSAEncryption
        # encrypt_fields = ("password",)
        # read_only_fields = ("avatar_url",)
        write_only_fields = ("password",)
        # extra_kwargs = {
        #     "password": {
        #         "write_only": True,
        #         "required": True,
        #     },
        # }

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
