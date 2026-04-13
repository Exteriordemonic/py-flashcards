from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.base import TemplateView

from decks.models import Deck

from flashcards.forms import (
    AnswerFormSet,
    FlashcardForm,
    FlashcardReviewForm,
)
from flashcards.mixins import CreatedByQuerysetMixin
from flashcards.models import Flashcard, Review
from flashcards.services import FlashcardService, AnswerInput


class FlashcardListView(LoginRequiredMixin, generic.ListView):
    model = Flashcard

    def get_queryset(self):
        return (
            Flashcard.objects.filter(created_by=self.request.user)
            .select_related("deck")
            .only("question", "deck_id", "deck__name")
        )


class FlashcardDetailView(LoginRequiredMixin, CreatedByQuerysetMixin, generic.DetailView):
    model = Flashcard

    def get_queryset(self):
        return super().get_queryset().prefetch_related("answers")


class FlashcardUpdateView(LoginRequiredMixin, CreatedByQuerysetMixin, generic.UpdateView):
    model = Flashcard
    form_class = FlashcardForm

    success_url = reverse_lazy("flashcards:flashcard-list")

    def get_context_data(self, **kwargs) -> dict[str]:
        context = super().get_context_data(**kwargs)
        if "formset" not in context:
            if self.request.method == "POST":
                context["formset"] = AnswerFormSet(self.request.POST)
            else:
                initial = [{"text": a.text, "is_correct": a.is_correct} for a in self.object.answers.order_by("pk")]
                context["formset"] = AnswerFormSet(initial=initial)
        return context

    def form_valid(self, form):
        formset = AnswerFormSet(self.request.POST)
        if not formset.is_valid():
            return self.form_invalid(form)

        question = form.cleaned_data.get("question")
        deck = form.cleaned_data.get("deck")
        answers = [AnswerInput(**answer) for answer in formset.cleaned_data if answer]

        try:
            self.object = FlashcardService.update_flashcard(self.object, question=question, deck=deck, answers=answers)
        except (ValueError, IntegrityError) as e:
            form.add_error(None, e)
            return self.form_invalid(form)
        else:
            return HttpResponseRedirect(self.get_success_url())

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["deck"].queryset = Deck.objects.filter(owner=self.request.user)
        return form


class FlashcardCreateView(LoginRequiredMixin, generic.CreateView):
    model = Flashcard
    form_class = FlashcardForm

    success_url = reverse_lazy("flashcards:flashcard-list")

    def get_context_data(self, **kwargs) -> dict[str]:
        context = super().get_context_data(**kwargs)
        if "formset" not in context:
            if self.request.method == "POST":
                context["formset"] = AnswerFormSet(self.request.POST)
            else:
                context["formset"] = AnswerFormSet()
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["deck"].queryset = Deck.objects.filter(owner=self.request.user)
        return form

    def form_valid(self, form):
        formset = AnswerFormSet(self.request.POST)
        if not formset.is_valid():
            return self.form_invalid(form)

        question = form.cleaned_data.get("question")
        deck = form.cleaned_data.get("deck")
        answers = [AnswerInput(**answer) for answer in formset.cleaned_data if answer]
        user = self.request.user

        try:
            flashcard = FlashcardService.create_flashcard(
                question=question, deck=deck, created_by=user, answers=answers
            )
            self.object = flashcard
        except (ValueError, IntegrityError) as e:
            form.add_error(None, e)
            return self.form_invalid(form)
        else:
            return HttpResponseRedirect(self.get_success_url())


class FlashcardDeleteView(LoginRequiredMixin, CreatedByQuerysetMixin, generic.DeleteView):
    model = Flashcard
    success_url = reverse_lazy("flashcards:flashcard-list")


class FlashcardReviewView(LoginRequiredMixin, CreatedByQuerysetMixin, generic.DetailView):
    model = Flashcard
    template_name = "flashcards/flashcard_review.html"

    def get_queryset(self):
        return super().get_queryset().prefetch_related("answers")

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
            is_correct = self.object.answers.filter(text=selected_answer, is_correct=True).exists()
            feedback_message = "Correct answer!" if is_correct else "Incorrect answer."

            Review.objects.create(
                flashcard=self.object,
                user=self.request.user,
                quality=(Review.Quality.PERFECT if is_correct else Review.Quality.HARD),
            )

        correct_answer_texts = list(self.object.answers.filter(is_correct=True).values_list("text", flat=True))

        context = self.get_context_data()
        context["form"] = form
        context["is_correct"] = is_correct
        context["correct_answer_texts"] = correct_answer_texts
        context["feedback_message"] = feedback_message

        return self.render_to_response(context)


class HomeView(TemplateView):
    template_name = "flashcards/home.html"
