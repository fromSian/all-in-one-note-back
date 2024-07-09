from .serializers import (
    NoteSerializer,
    NoteItemSerializer,
    NoteItemIndependentSerializer,
)
from .models import Note, NoteItem
from .filters import NoteFilter, NoteItemFilter

from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
    UpdateModelMixin,
    RetrieveModelMixin,
)
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.renderers import JSONRenderer
from drf_yasg.utils import swagger_auto_schema

# Create your views here.

"""note"""


class NoteViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = NoteFilter

    def get_queryset(self):
        user = self.request.user
        return Note.objects.filter(user=user).order_by("-updated")

    def get_serializer_class(self):
        return NoteSerializer

    """
    query note list
    pagination
    side date line

    response includes 'title' 'created' 'updated' 'summary' 'note_list_count
    """

    """
    create a note

    params={
        'title': '',
        'note_items': [
            {
                'content': ''
            },
    }
    """
    """
    update title
    """
    """
    delete a note
    """

    """
    query note detail note_list

    params note 'id'

    pagination

    response includes 'content' 'sort' 'created' 'updated'
    """

    # @action(detail=True, methods=["GET"])
    # def section(self, request, *args, **kwargs):
    #     try:
    #         note = self.get_object()
    #         page = self.paginate_queryset(note.note_items)
    #         if page is not None:
    #             serializer = NoteItemSerializer(page, many=True)
    #             return self.get_paginated_response(serializer.data)
    #         else:
    #             serializer = NoteItemSerializer(note.note_items, many=True)
    #             return Response(serializer.data, status=status.HTTP_200_OK)
    #     except Exception as e:
    #         return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    """
    haven't finish
    '全量替换‘
    update a note

    deleted_note_id
    note_items: 
    {
    id: {
    content
    }
    }
    if no id is removed

    to new add note_item must setting the id with 'add_1/2/3/4'

    will replace the sort but later write this part.
    """

    # def update(self, request, *args, **kwargs):
    #     return super().update(request, *args, **kwargs)


class NoteItemViewSet(
    ListModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    queryset = NoteItem.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return NoteItemIndependentSerializer
        else:
            return NoteItemSerializer

    filterset_class = NoteItemFilter

    """
    create one note_item to a note
    the sort is added
    """

    """
    update one note item
    """

    """
    delete a note item
    """
