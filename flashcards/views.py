from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView


from flashcards.mixins import OwnerRequiredMixin, CreatedByRequiredMixin
from flashcards.models import Deck, Flashcard
from flashcards.forms import FlashcardForm, DeckForm


class FlashcardListView(LoginRequiredMixin, generic.ListView):
    model = Flashcard

    def get_queryset(self):
        return Flashcard.objects.filter(
            created_by=self.request.user
        ).prefetch_related("deck")


class FlashcardDetailView(
    LoginRequiredMixin, CreatedByRequiredMixin, generic.DetailView
):
    model = Flashcard


class FlashcardUpdateView(
    LoginRequiredMixin, CreatedByRequiredMixin, generic.UpdateView
):
    model = Flashcard
    form_class = FlashcardForm

    success_url = reverse_lazy("flashcards:flashcard-list")


class FlashcardCreateView(LoginRequiredMixin, generic.CreateView):
    model = Flashcard
    form_class = FlashcardForm

    success_url = reverse_lazy("flashcards:flashcard-list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class FlashcardDeleteView(
    LoginRequiredMixin, CreatedByRequiredMixin, generic.DeleteView
):
    model = Flashcard
    success_url = reverse_lazy("flashcards:flashcard-list")


class DeckListView(LoginRequiredMixin, generic.ListView):
    model = Deck

    def get_queryset(self):
        return Deck.objects.filter(members=self.request.user)


class DeckDetailView(
    LoginRequiredMixin, OwnerRequiredMixin, generic.DetailView
):
    model = Deck

    def get_context_data(self, **kwargs):
        current_user = self.request.user

        context = super().get_context_data(**kwargs)
        deck = self.object
        context["is_deck_owner"] = deck.owner_id == self.request.user.pk
        context["is_member"] = deck.members.filter(pk=current_user.pk).exists()

        return context


class DeckUpdateView(
    LoginRequiredMixin, OwnerRequiredMixin, generic.UpdateView
):
    model = Deck
    form_class = DeckForm
    success_url = reverse_lazy("flashcards:deck-list")


class DeckCreateView(LoginRequiredMixin, generic.CreateView):
    model = Deck
    form_class = DeckForm
    success_url = reverse_lazy("flashcards:deck-list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class DeckDeleteView(
    LoginRequiredMixin, OwnerRequiredMixin, generic.DeleteView
):
    model = Deck
    success_url = reverse_lazy("flashcards:deck-list")


class HomeView(TemplateView):
    template_name = "flashcards/home.html"
