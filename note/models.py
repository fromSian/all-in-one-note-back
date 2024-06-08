from django.db import models
from account.models import User
# Create your models here.

class Note(models.Model):
    title = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, verbose_name="create time")
    updated = models.DateTimeField(auto_now_add=True, verbose_name="update time")

class NoteItem(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    content = models.TextField()
    sort = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True, verbose_name="create time")
    updated = models.DateTimeField(auto_now_add=True, verbose_name="update time")


