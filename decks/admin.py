from django.contrib import admin

from decks.models import Deck


@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    list_display = ("name", "owner")
    search_fields = ("name", "owner__username")
    list_filter = ("owner",)
