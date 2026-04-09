from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from django.db import IntegrityError, transaction


from flashcards.mixins import CreatedByQuerysetMixin, OwnerQuerysetMixin
from flashcards.models import Deck, Flashcard, Review
from flashcards.forms import (
    FlashcardForm,
    DeckForm,
    FlashcardDeckForm,
    FlashcardReviewForm,
)

FLASHCARD_DUPLICATE_ERROR = (
    "Flashcard with this question already exists in this deck."
)


class FlashcardListView(LoginRequiredMixin, generic.ListView):
    model = Flashcard

    def get_queryset(self):
        return (
            Flashcard.objects.filter(created_by=self.request.user)
            .select_related("deck")
            .only("question", "deck_id", "deck__name")
        )


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
        try:
            with transaction.atomic():
                return super().form_valid(form)
        except IntegrityError:
            form.add_error("question", FLASHCARD_DUPLICATE_ERROR)
            return self.form_invalid(form)


class FlashcardDeleteView(
    LoginRequiredMixin, CreatedByQuerysetMixin, generic.DeleteView
):
    model = Flashcard
    success_url = reverse_lazy("flashcards:flashcard-list")


class FlashcardReviewView(
    LoginRequiredMixin, CreatedByQuerysetMixin, generic.DetailView
):
    model = Flashcard
    template_name = "flashcards/flashcard_review.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = FlashcardReviewForm(flashcard=self.object)

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = FlashcardReviewForm(request.POST, flashcard=self.object)

        is_correct = None
        feedback_message = ""
        if form.is_valid():
            selected_answer = form.cleaned_data["selected_answer"]
            is_correct = selected_answer == self.object.correct_answer
            feedback_message = (
                "Correct answer!" if is_correct else "Incorrect answer."
            )

        context = self.get_context_data()
        context["form"] = form
        context["is_correct"] = is_correct
        context["correct_answer"] = self.object.correct_answer
        context["feedback_message"] = feedback_message

        Review.objects.create(
            flashcard=self.object,
            user=self.request.user,
            quality=(
                Review.Quality.PERFECT if is_correct else Review.Quality.HARD
            ),
        )

        return self.render_to_response(context)


class DeckListView(LoginRequiredMixin, OwnerQuerysetMixin, generic.ListView):
    model = Deck

    def get_queryset(self):
        return super().get_queryset().prefetch_related("flashcards")


class DeckDetailView(
    LoginRequiredMixin, OwnerQuerysetMixin, generic.DetailView
):
    model = Deck

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["flashcards"] = self.object.flashcards.filter(
            created_by=self.request.user
        )

        context["form_create_flashcard"] = kwargs.get(
            "form_create_flashcard", FlashcardDeckForm()
        )

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

            return redirect("flashcards:deck-detail", pk=self.object.pk)

        context = self.get_context_data(form_create_flashcard=form)
        return self.render_to_response(context)


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
