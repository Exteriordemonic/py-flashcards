from django.contrib import admin

from flashcards.models import Answer, Flashcard, FlashcardUserState

admin.site.register(Flashcard)
admin.site.register(Answer)
admin.site.register(FlashcardUserState)
