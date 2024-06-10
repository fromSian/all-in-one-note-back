from .serializers import (
    NoteSerializer,
    NoteItemSerializer,
    NoteWithNoteItemWriteSerializer,
)
from .models import Note, NoteItem

from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
    UpdateModelMixin,
    RetrieveModelMixin,
)
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.renderers import JSONRenderer

# Create your views here.

class NoteViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    queryset = Note.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return NoteWithNoteItemWriteSerializer
        else:
            return NoteSerializer

    """
    query note list
    pagination
    side date line

    response includes 'title' 'created' 'updated' 'summary' 'note_list_count
    """

    """
    query note detail note_list

    params note 'id'

    pagination

    response includes 'content' 'sort' 'created' 'updated'
    """

    # @action(detail=True, methods=["GET"])
    # def items(self, request, *args, **kwargs):
    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)

    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(True)
    #     try:
    #         note = self.get_object()
    #         page = self.paginate_queryset(note.note_items)
    #         if page is not None:
    #             serializer = NoteItemSerializer(page, many=True)
    #             return self.get_paginated_response(serializer.data)
    #         else:

    #         serializer = NoteItemSerializer(note.note_items, many=True)
    #         return Response(serializer.data)
    #     except Exception as e:
    #         pass

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


# class NoteViewSet(ModelViewSet):
#     queryset = Note.objects.all()
#     serializer_class = NoteSerializer
#     permission_classes = [permissions.IsAuthenticated]


"""
set local and production env to config.settings
"""


class NoteItemViewSet(ModelViewSet):
    queryset = NoteItem.objects.all()
    serializer_class = NoteItemSerializer


"""note"""


"""
create one note_item to a note

the sort is added
"""

"""
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

"""
update title
"""

"""
update one note item
"""

"""
delete a note item
"""

"""
delete a note
"""
