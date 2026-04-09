from django.contrib import admin

# Register your models here.
from .models import Flashcard, Deck

admin.site.register(Flashcard)


@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    list_display = ("name", "owner")
    search_fields = ("name", "owner__username")
    list_filter = ("owner",)
