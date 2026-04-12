from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, transaction
from django.db.models import Count
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic

from flashcards.constants import FLASHCARD_DUPLICATE_ERROR
from flashcards.forms import FlashcardDeckForm

from decks.forms import DeckForm
from decks.mixins import OwnerQuerysetMixin
from decks.models import Deck


class DeckListView(LoginRequiredMixin, OwnerQuerysetMixin, generic.ListView):
    model = Deck
    template_name = "decks/deck_list.html"

    def get_queryset(self):
        return super().get_queryset().annotate(flashcards_count=Count("flashcards")).only("id", "name", "owner")


class DeckDetailView(LoginRequiredMixin, OwnerQuerysetMixin, generic.DetailView):
    model = Deck
    template_name = "decks/deck_detail.html"

    def get_queryset(self):
        return super().get_queryset().prefetch_related("flashcards").only("name", "flashcards__question")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["flashcards"] = self.object.flashcards.filter(created_by=self.request.user)

        context["form_create_flashcard"] = kwargs.get("form_create_flashcard", FlashcardDeckForm())

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()  # Deck

        form = FlashcardDeckForm(request.POST)

        if form.is_valid():
            flashcard = form.save(commit=False)
            flashcard.deck = self.object
            flashcard.created_by = request.user
            try:
                with transaction.atomic():
                    flashcard.save()
            except IntegrityError:
                form.add_error("question", FLASHCARD_DUPLICATE_ERROR)
                context = self.get_context_data(form_create_flashcard=form)
                return self.render_to_response(context)

            return redirect("decks:deck-detail", pk=self.object.pk)

        context = self.get_context_data(form_create_flashcard=form)
        return self.render_to_response(context)


class DeckUpdateView(LoginRequiredMixin, OwnerQuerysetMixin, generic.UpdateView):
    model = Deck
    form_class = DeckForm
    template_name = "decks/deck_form.html"
    success_url = reverse_lazy("decks:deck-list")


class DeckCreateView(LoginRequiredMixin, generic.CreateView):
    model = Deck
    form_class = DeckForm
    template_name = "decks/deck_form.html"
    success_url = reverse_lazy("decks:deck-list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class DeckDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Deck
    template_name = "decks/deck_confirm_delete.html"
    success_url = reverse_lazy("decks:deck-list")

    def get_queryset(self):
        return Deck.objects.prefetch_related("flashcards").filter(
            owner=self.request.user,
        )
