from .serializers import (
    NoteSerializer,
    NoteItemSerializer,
    NoteItemIndependentSerializer,
)
from .models import Note, NoteItem
from .filters import NoteFilter, NoteItemFilter
from utils.permission import RequestValidPermission
from utils.encryption import AESEncryption
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
from drf_yasg import openapi
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

# Create your views here.

"""note"""


class SinceIdPageListMixin:
    @swagger_auto_schema(
        operation_description="since id page list",
        manual_parameters=[
            openapi.Parameter(
                "since_id",
                openapi.IN_QUERY,
                description="since_id",
                type=openapi.TYPE_NUMBER,
            ),
            openapi.Parameter(
                "size",
                openapi.IN_QUERY,
                description="size",
                type=openapi.TYPE_NUMBER,
            ),
        ],
        responses={
            status.HTTP_200_OK: openapi.Response(
                "success", examples={"message": "success"}
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                "fail", examples={"message": "fail"}
            ),
        },
    )
    def list(self, request, *args, **kwargs):
        since_id = request.query_params.get("since_id", "")
        size = int(request.query_params.get("size", "")) | 10
        queryset = self.filter_queryset(self.get_queryset())
        start = 0
        if since_id:
            since_object = queryset.filter(id=since_id).first()
            if since_object:
                start = list(queryset).index(since_object) + 1
        count = len(queryset)
        page_queryset = queryset[start : start + size]
        hasNext = start + size < count

        serializer = self.get_serializer(page_queryset, many=True)
        return Response(
            {"results": serializer.data, "count": count, "hasNext": hasNext}
        )


class NoteViewSet(
    SinceIdPageListMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    permission_classes = [RequestValidPermission, permissions.IsAuthenticated]
    filterset_class = NoteFilter

    def get_queryset(self):
        user = self.request.user
        return Note.objects.filter(user=user).order_by("-updated")

    def get_serializer_class(self):
        return NoteSerializer


from django_filters.rest_framework import DjangoFilterBackend


class NoteItemFilterBackend(DjangoFilterBackend):
    def get_filterset_class(self, view, queryset):
        if view.action == "list":
            return NoteItemFilter
        return super().get_filterset_class(view, queryset)


class NoteItemViewSet(
    SinceIdPageListMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):

    filter_backends = [NoteItemFilterBackend]
    permission_classes = [RequestValidPermission, permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return NoteItemIndependentSerializer
        else:
            return NoteItemSerializer

    def get_queryset(self):
        user = self.request.user
        return NoteItem.objects.filter(note__user=user)


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
@permission_classes([RequestValidPermission, permissions.IsAuthenticated])
@api_view(["POST"])
def note_content_md(request):
    try:
        user = request.user
        id = request.data.get("id")
        timezone = request.data.get("timezone", "Asia/Shanghai")
        note = Note.objects.filter(id=id).first()
        if not note:
            raise ValidationError(_("Note not found"))
        if note.user != user:
            raise ValidationError(_("you are not allowed to operate this note"))

        encryption = AESEncryption()
        order = request.data.get("order", "-created")
        order = "-created" if not order else order
        note_items = NoteItem.objects.filter(note__id=id).order_by(order)
        markdown_content = """# {0} \n\n<div style='display: flex; justify-content: end; color: #8da2b8; font-size: 10px'>{1} {2}</div>\n\n""".format(
            encryption.decrypt(note.title) if note.title else "",
            localtime(note.created, ZoneInfo(timezone)).strftime(
                "%Y-%m-%d %H:%M:%S %z"
            ),
            localtime(note.updated, ZoneInfo(timezone)).strftime(
                "%Y-%m-%d %H:%M:%S %z"
            ),
        )
        for note_item in note_items:
            markdown_content += (
                md(
                    encryption.decrypt(note_item.content) if note_item.content else "",
                    heading_style="ATX",
                )
                + "<div style='display: flex; justify-content: end; color: #8da2b8; font-size: 10px'>{0} {1}</div>\n\n".format(
                    localtime(note_item.created, ZoneInfo(timezone)).strftime(
                        "%Y-%m-%d %H:%M:%S %z"
                    ),
                    localtime(note_item.updated, ZoneInfo(timezone)).strftime(
                        "%Y-%m-%d %H:%M:%S %z"
                    ),
                )
                + "<div style='border: dashed 1px rgba(255, 255, 255, 0.2); margin: 8px 0px;'></div>\n\n"
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
        print(e)
        return Response(
            {"message": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )
