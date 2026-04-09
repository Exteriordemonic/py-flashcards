from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView


from flashcards.mixins import CreatedByQuerysetMixin, OwnerQuerysetMixin
from flashcards.models import Deck, Flashcard
from flashcards.forms import FlashcardDeckForm, FlashcardForm, DeckForm


class FlashcardListView(LoginRequiredMixin, generic.ListView):
    model = Flashcard

    def get_queryset(self):
        return Flashcard.objects.filter(
            created_by=self.request.user
        ).select_related("deck")


class FlashcardDetailView(
    LoginRequiredMixin, CreatedByQuerysetMixin, generic.DetailView
):
    model = Flashcard


class FlashcardUpdateView(
    LoginRequiredMixin, CreatedByQuerysetMixin, generic.UpdateView
):
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


class FlashcardDeleteView(
    LoginRequiredMixin, CreatedByQuerysetMixin, generic.DeleteView
):
    model = Flashcard
    success_url = reverse_lazy("flashcards:flashcard-list")


class DeckListView(LoginRequiredMixin, OwnerQuerysetMixin, generic.ListView):
    model = Deck


class DeckDetailView(
    LoginRequiredMixin, OwnerQuerysetMixin, generic.DetailView
):
    model = Deck

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["flashcards"] = self.object.flashcards.filter(
            created_by=self.request.user
        )

        context["form_crate_flashcard"] = FlashcardDeckForm

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()  # Deck

        form = FlashcardDeckForm(request.POST)

        if form.is_valid():
            flashcard = form.save(commit=False)
            flashcard.deck = self.object
            flashcard.created_by = request.user
            flashcard.save()

        return redirect("flashcards:deck-detail", pk=self.object.pk)


class DeckUpdateView(
    LoginRequiredMixin, OwnerQuerysetMixin, generic.UpdateView
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


class DeckDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Deck
    success_url = reverse_lazy("flashcards:deck-list")

    def get_queryset(self):
        return Deck.objects.prefetch_related("flashcards").filter(
            owner=self.request.user,
        )


class HomeView(TemplateView):
    template_name = "flashcards/home.html"
