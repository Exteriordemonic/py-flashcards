from django.urls import reverse_lazy
from django.views import generic

from flashcards.models import Flashcard


class FlashcardListView(generic.ListView):
    model = Flashcard


class FlashcardDetailView(generic.DetailView):
    model = Flashcard


class FlashcardUpdateView(generic.UpdateView):
    model = Flashcard


class FlashcardCreateView(generic.CreateView):
    model = Flashcard
    fields = "__all__"
    success_url = reverse_lazy("flashcards:flashcard-list")


class FlashcardDeleteView(generic.DeleteView):
    model = Flashcard
