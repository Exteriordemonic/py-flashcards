from django.contrib import admin

# Register your models here.
from .models import Flashcard, Deck

admin.site.register(Flashcard)
admin.site.register(Deck)
