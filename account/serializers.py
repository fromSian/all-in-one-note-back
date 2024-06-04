from rest_framework import serializers
from utils.mixin.EncryptSerializerMixin import EncryptSerializerMixin
from .models import User
from django.contrib.auth.models import Group


class UserSerializer(EncryptSerializerMixin, serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "email",
            "password",
        ]
        # encrypt_fields = ("password",)

    def create(self, validated_data):
        normal = Group.objects.filter(name="front").first()
        if not normal:
            normal = Group.objects.create(name="front")
        user = User.objects.create_user(**validated_data)
        user.groups.add(normal)
        return user

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            if key == "password":
                instance.set_password(value)
            else:
                setattr(instance, key, value)
        instance.save()
        return instance
