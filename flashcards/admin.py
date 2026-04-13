from django.contrib import admin

from flashcards.models import Answer, Flashcard

admin.site.register(Flashcard)
admin.site.register(Answer)
