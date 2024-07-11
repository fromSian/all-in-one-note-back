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
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.renderers import JSONRenderer
from drf_yasg.utils import swagger_auto_schema
from django.core.exceptions import ValidationError

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


from django_filters.rest_framework import DjangoFilterBackend


class NoteItemFilterBackend(DjangoFilterBackend):
    def get_filterset_class(self, view, queryset):
        if view.action == "list":
            return NoteItemFilter
        return super().get_filterset_class(view, queryset)

    # def get_filterset_kwargs(self, request, queryset, view):
    #     kwargs = super().get_filterset_kwargs(request, queryset, view)

    #     # merge filterset kwargs provided by view class
    #     if hasattr(view, "get_filterset_kwargs"):
    #         kwargs.update(view.get_filterset_kwargs())

    #     return kwargs


class NoteItemViewSet(
    ListModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):

    filter_backends = [NoteItemFilterBackend]

    def get_serializer_class(self):
        if self.action == "create":
            return NoteItemIndependentSerializer
        else:
            return NoteItemSerializer

    def get_queryset(self):
        user = self.request.user
        return NoteItem.objects.filter(note__user=user)

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


from markdownify import markdownify as md
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.timezone import localtime
from zoneinfo import ZoneInfo


@swagger_auto_schema(
    method="POST",
    operation_description="get markdown content",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["id"],
        properties={
            "id": openapi.Schema(type=openapi.TYPE_NUMBER, description="note id"),
            "order": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="order",
            ),
        },
    ),
    responses={
        status.HTTP_200_OK: openapi.Response(
            "success", examples={"message": "success"}
        ),
        status.HTTP_400_BAD_REQUEST: openapi.Response(
            "fail", examples={"message": "fail"}
        ),
    },
)
@permission_classes([permissions.IsAuthenticated])
@api_view(["POST"])
def note_content_md(request):
    try:
        user = request.user
        id = request.data.get("id")
        note = Note.objects.filter(id=id).first()

        if not note:
            raise ValidationError("Note not found")
        if note.user != user:
            raise ValidationError("Permission denied")

        order = request.data.get("order", "-created")
        order = "-created" if not order else order
        note_items = NoteItem.objects.filter(note__id=id).order_by(order)
        markdown_content = ""
        for note_item in note_items:
            markdown_content += (
                "<font size=1 color=#8da2b8>{0}</font>\n\n".format(
                    localtime(note_item.created, ZoneInfo("Asia/Shanghai")).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                )
                + md(note_item.content, heading_style="ATX")
                + "\n\n"
            )
        return Response(
            {"content": markdown_content},
            status=status.HTTP_200_OK,
        )
    except ValidationError as e:
        print(e)
        return Response(
            {"message": e.message},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        return Response(
            {"message": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )
