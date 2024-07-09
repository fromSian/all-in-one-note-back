from django.db import models
from account.models import User

# Create your models here.


class Note(models.Model):
    title = models.CharField(max_length=255, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, verbose_name="create time")
    updated = models.DateTimeField(auto_now=True, verbose_name="update time")
    summary = models.TextField(blank=True)

    @property
    def note_items(self):
        return NoteItem.objects.filter(note=self)

    def note_items_count(self):
        return self.note_items.count()

    """
    later
    write in view function
    base on the bytes length
    """

    def summary(self):
        # calculate the text bytes length
        # string = 'fks juries分开来说'
        # len(string.encode('utf-8'))
        return self.note_items.first().summary if self.note_items else ""

    def __str__(self) -> str:
        return self.titlex


class NoteItem(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    content = models.TextField()
    summary = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name="create time")
    updated = models.DateTimeField(auto_now=True, verbose_name="update time")

    def __str__(self) -> str:
        return self.content
