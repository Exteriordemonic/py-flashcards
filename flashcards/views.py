from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView


from flashcards.models import Deck, Flashcard
from flashcards.forms import FlashcardForm, DeckForm


class FlashcardListView(LoginRequiredMixin, generic.ListView):
    model = Flashcard

    def get_queryset(self):
        return Flashcard.objects.filter(
            created_by=self.request.user
        ).select_related("deck")


class FlashcardDetailView(LoginRequiredMixin, generic.DetailView):
    model = Flashcard


class FlashcardUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Flashcard
    form_class = FlashcardForm

    success_url = reverse_lazy("flashcards:flashcard-list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["deck"].queryset = Deck.objects.filter(
            owner=self.request.user
        )
        return form


class FlashcardCreateView(LoginRequiredMixin, generic.CreateView):
    model = Flashcard
    form_class = FlashcardForm

    success_url = reverse_lazy("flashcards:flashcard-list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["deck"].queryset = Deck.objects.filter(
            owner=self.request.user
        )
        return form

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class FlashcardDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Flashcard
    success_url = reverse_lazy("flashcards:flashcard-list")


class DeckListView(LoginRequiredMixin, generic.ListView):
    model = Deck

    def get_queryset(self):
        return Deck.objects.prefetch_related("flashcards").filter(
            owner=self.request.user
        )


class DeckDetailView(LoginRequiredMixin, generic.DetailView):
    model = Deck

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        deck = self.object
        context["is_deck_owner"] = deck.owner_id == self.request.user.pk

        return context


class DeckUpdateView(LoginRequiredMixin, generic.UpdateView):
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


class DeckDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Deck
    success_url = reverse_lazy("flashcards:deck-list")


class HomeView(TemplateView):
    template_name = "flashcards/home.html"
