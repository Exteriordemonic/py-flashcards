from django.urls import path

from flashcards.views import (
    FlashcardCreateView,
    FlashcardDeleteView,
    FlashcardDetailView,
    FlashcardListView,
    FlashcardReviewView,
    FlashcardUpdateView,
)

urlpatterns = [
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
    path(
        "<int:pk>/review/",
        FlashcardReviewView.as_view(),
        name="flashcard-review",
    ),
]
