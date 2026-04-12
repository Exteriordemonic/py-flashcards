import random

from django import forms

from flashcards.models import Flashcard, Answer


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = [
            "text",
            "is_correct",
        ]


class FlashcardForm(forms.ModelForm):
    class Meta:
        model = Flashcard
        fields = [
            "question",
            "deck",
        ]


class FlashcardDeckForm(FlashcardForm):
    class Meta:
        model = Flashcard
        fields = [
            "question",
        ]


class FlashcardReviewForm(forms.Form):
    selected_answer = forms.ChoiceField(
        choices=[],
        widget=forms.RadioSelect,
        label="Choose Answer",
    )

    def __init__(self, *args, flashcard=None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if flashcard:
            texts = list(flashcard.answers.order_by("pk").values_list("text", flat=True))
            choices = [(t, t) for t in texts]

            # Shuffle only on initial display (GET). Keep stable order on POST.
            if not self.is_bound:
                random.shuffle(choices)

            self.fields["selected_answer"].choices = choices
