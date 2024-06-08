from .serializers import NoteSerializer, NoteItemWriteSerializer
from .models import Note, NoteItem

from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
# Create your views here.


class NoteViewSet(ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]


class NoteItemViewSet(ModelViewSet):
    queryset = NoteItem.objects.all()
    serializer_class = NoteItemWriteSerializer
    