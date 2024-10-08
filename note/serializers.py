from rest_framework import serializers
from .models import Note, NoteItem
from utils.encryption import AESEncryption
from utils.serializers import EncryptSerializerMixin


class NoteItemSerializer(EncryptSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = NoteItem
        fields = ("id", "content", "note", "created", "updated", "summary")
        read_only_fields = ["id", "created", "updated", "note"]
        encryption_class = AESEncryption
        encrypt_fields = ("content", "summary")


class NoteItemIndependentSerializer(
    EncryptSerializerMixin, serializers.ModelSerializer
):
    class Meta:
        model = NoteItem
        fields = ("id", "content", "note", "created", "updated", "summary")
        read_only_fields = [
            "id",
            "created",
            "updated",
        ]
        encryption_class = AESEncryption
        encrypt_fields = ("content", "summary")

        # validate note user is the same


class NoteSerializer(EncryptSerializerMixin, serializers.ModelSerializer):

    class Meta:
        model = Note
        fields = (
            "id",
            "title",
            "summary",
            "count",
            "created",
            "updated",
            "user",
        )
        read_only_fields = [
            "id",
            "created",
            "summary",
            "updated",
            "count",
            "user",
        ]
        encryption_class = AESEncryption
        encrypt_fields = ("summary", "title")

    def create(self, validated_data):
        user = self.context["request"].user
        note = Note.objects.create(user=user, **validated_data)
        return note

    def update(self, instance, validated_data):
        user = self.context["request"].user
        if user != instance.user:
            raise serializers.ValidationError("Permission denied")
        return super().update(instance, validated_data)


# class NoteWithNoteItemWriteSerializer(
#     EncryptSerializerMixin, serializers.ModelSerializer
# ):
#     note_list = NoteItemSerializer(source="note_items", many=True)

#     class Meta:
#         model = Note
#         fields = ["title", "note_list"]
#         encryption_class = AESEncryption
#         encryption_class = ("title",)

#     def create(self, validated_data):
#         user = self.context["request"].user
#         note_list = validated_data.pop("note_items", [])
#         print(user, validated_data)
#         note = Note.objects.create(user=user, **validated_data)
#         for note_item in note_list:
#             NoteItem.objects.create(
#                 note=note, sort=note_list.index(note_item), **note_item
#             )
#         return note
