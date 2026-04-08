from django.urls import path

from flashcards.views import (
    FlashcardCreateView,
    FlashcardListView,
    FlashcardDetailView,
    FlashcardUpdateView,
    FlashcardDeleteView,
    DeckListView,
    DeckCreateView,
    DeckDetailView,
    DeckUpdateView,
    DeckDeleteView,
    deck_add,
    deck_remove,
)


urlpatterns = [
    # Flashcards
    path("", FlashcardListView.as_view(), name="flashcard-list"),
    path("create/", FlashcardCreateView.as_view(), name="flashcard-create"),
    path("<int:pk>/", FlashcardDetailView.as_view(), name="flashcard-detail"),
    path(
        "<int:pk>/update/",
        FlashcardUpdateView.as_view(),
        name="flashcard-update",
    ),
    path(
        "<int:pk>/delete/",
        FlashcardDeleteView.as_view(),
        name="flashcard-delete",
    ),
    # Decks
    path("decks/", DeckListView.as_view(), name="deck-list"),
    path("decks/create", DeckCreateView.as_view(), name="deck-create"),
    path("decks/<int:pk>/", DeckDetailView.as_view(), name="deck-detail"),
    path(
        "decks/<int:pk>/update/",
        DeckUpdateView.as_view(),
        name="deck-update",
    ),
    path(
        "decks/<int:pk>/delete/",
        DeckDeleteView.as_view(),
        name="deck-delete",
    ),
    # Functional
    path("deck/<int:pk>/add/", deck_add, name="deck-add"),
    path("deck/<int:pk>/remove/", deck_remove, name="deck-remove"),
]
