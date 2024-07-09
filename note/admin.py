from django.contrib import admin
from .models import Note, NoteItem

# Register your models here.


class NoteAdmin(admin.ModelAdmin):
    list_display = ("title", "created", "updated", "user")


admin.site.register(Note, NoteAdmin)
