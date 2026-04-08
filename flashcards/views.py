import keyword
from django.contrib.auth.views import login_required
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from django.shortcuts import redirect


from flashcards.models import Deck, Flashcard


class FlashcardListView(LoginRequiredMixin, generic.ListView):
    model = Flashcard

    def get_queryset(self):
        return Flashcard.objects.filter(
            created_by=self.request.user
        ).prefetch_related("deck")


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

    def get_queryset(self):
        return Deck.objects.filter(members=self.request.user)


class DeckDetailView(LoginRequiredMixin, generic.DetailView):
    model = Deck

    def get_context_data(self, **kwargs):
        current_user = self.request.user

        context = super().get_context_data(**kwargs)
        deck = self.object
        context["is_deck_owner"] = deck.owner_id == self.request.user.pk
        context["is_member"] = deck.members.filter(pk=current_user.pk).exists()

        return context


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


@login_required
def deck_add(request, pk):
    current_user = request.user
    Deck.objects.get(id=pk).members.add(current_user)
    return redirect("flashcards:deck-detail", pk=pk)


@login_required
def deck_remove(request, pk):
    current_user = request.user
    Deck.objects.get(id=pk).members.remove(current_user)
    return redirect("flashcards:deck-detail", pk=pk)


class HomeView(TemplateView):
    template_name = "flashcards/home.html"
