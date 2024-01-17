from django.contrib import admin

from api.models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    pass
