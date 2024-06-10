from rest_framework import serializers
from .models import Note, NoteItem
from utils.encryption import AESEncryption
from utils.serializers import EncryptSerializerMixin

class NoteItemSerializer(EncryptSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = NoteItem
        fields = ("id", "content", "note", "created", "updated", "sort")
        read_only_fields = ["id", "sort", "created", "updated", "sort", "note"]
        encryption_class = AESEncryption
        encrypt_fields = ("content",)


class NoteSerializer(EncryptSerializerMixin, serializers.ModelSerializer):

    class Meta:
        model = Note
        fields = (
            "id",
            "title",
            "summary",
            "note_items_count",
            "created",
            "updated",
        )
        read_only_fields = ["id", "created", "updated", "summary", "note_items_count"]
        encryption_class = AESEncryption
        encrypt_fields = ("title", "summary")


class NoteWithNoteItemWriteSerializer(
    EncryptSerializerMixin, serializers.ModelSerializer
):
    note_list = NoteItemSerializer(source="note_items", many=True)

    class Meta:
        model = Note
        fields = ["title", "note_list"]
        encryption_class = AESEncryption
        encryption_class = ("title",)

    def create(self, validated_data):
        user = self.context["request"].user
        note_list = validated_data.pop("note_items", [])
        print(user, validated_data)
        note = Note.objects.create(user=user, **validated_data)
        for note_item in note_list:
            NoteItem.objects.create(
                note=note, sort=note_list.index(note_item), **note_item
            )
        return note
