from rest_framework import serializers
from .models import Note, NoteItem
from utils.encryption import AESEncryption
from utils.serializers import EncryptSerializerMixin


class NoteItemWriteSerializer(EncryptSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = NoteItem
        fields = ("note", "content")

    def create(self, validated_data):
        print(validated_data)
        note = validated_data["note"]
        print(note.user)
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

class NoteItemInNoteSerializer(EncryptSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = NoteItem
        fields = ("id", "content", "created", "updated", "sort")
        read_only_fields = ["id", "sort", "created", "updated", "sort"]
        encryption_class = AESEncryption
        encrypt_fields = ("content",)


class NoteSerializer(serializers.ModelSerializer):
    note_list = NoteItemInNoteSerializer(many=True, source="note_items")

    class Meta:
        model = Note
        fields = ("id", "title", "note_list")

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

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
