from django.db import models
from account.models import User

# Create your models here.


class Note(models.Model):
    title = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, verbose_name="create time")
    updated = models.DateTimeField(auto_now_add=True, verbose_name="update time")

    @property
    def note_items(self):
        return NoteItem.objects.filter(note=self).order_by("sort")

    def note_items_count(self):
        return self.note_items.count()


    '''
    later
    write in view function
    base on the bytes length
    '''
    def summary(self):
        # calculate the text bytes length
        # string = 'fks juries分开来说'
        # len(string.encode('utf-8'))
        return (
            self.note_items.first().content if self.note_items.first() else ""
        )

    def __str__(self) -> str:
        return self.title


class NoteItem(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    content = models.TextField()
    sort = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True, verbose_name="create time")
    updated = models.DateTimeField(auto_now_add=True, verbose_name="update time")

    def __str__(self) -> str:
        return self.content
