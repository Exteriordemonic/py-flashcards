from django.urls import path

from decks.views import (
    DeckCreateView,
    DeckDeleteView,
    DeckDetailView,
    DeckListView,
    DeckUpdateView,
)

app_name = "decks"

urlpatterns = [
    path("", DeckListView.as_view(), name="deck-list"),
    path("create", DeckCreateView.as_view(), name="deck-create"),
    path("<int:pk>/", DeckDetailView.as_view(), name="deck-detail"),
    path(
        "<int:pk>/update/",
        DeckUpdateView.as_view(),
        name="deck-update",
    ),
    path(
        "<int:pk>/delete/",
        DeckDeleteView.as_view(),
        name="deck-delete",
    ),
]
