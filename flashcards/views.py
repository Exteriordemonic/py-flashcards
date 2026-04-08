from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView


from flashcards.models import Deck, Flashcard


class FlashcardListView(LoginRequiredMixin, generic.ListView):
    model = Flashcard


class FlashcardDetailView(LoginRequiredMixin, generic.DetailView):
    model = Flashcard


class FlashcardUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Flashcard
    fields = "__all__"
    success_url = reverse_lazy("flashcards:flashcard-list")


class FlashcardCreateView(LoginRequiredMixin, generic.CreateView):
    model = Flashcard
    fields = "__all__"
    success_url = reverse_lazy("flashcards:flashcard-list")


class FlashcardDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Flashcard
    success_url = reverse_lazy("flashcards:flashcard-list")


class DeckListView(LoginRequiredMixin, generic.ListView):
    model = Deck


class DeckDetailView(LoginRequiredMixin, generic.DetailView):
    model = Deck


class DeckUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Deck
    fields = "__all__"
    success_url = reverse_lazy("flashcards:deck-list")


class DeckCreateView(LoginRequiredMixin, generic.CreateView):
    model = Deck
    fields = "__all__"
    success_url = reverse_lazy("flashcards:deck-list")


class DeckDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Deck
    success_url = reverse_lazy("flashcards:deck-list")


class HomeView(TemplateView):
    template_name = "flashcards/home.html"
