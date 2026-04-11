import random

from django import forms

from flashcards.models import Flashcard


class FlashcardForm(forms.ModelForm):
    CORRECT_CHOICES = [
        ("A", "A"),
        ("B", "B"),
        ("C", "C"),
        ("D", "D"),
    ]

    correct_answer = forms.ChoiceField(
        choices=CORRECT_CHOICES, widget=forms.RadioSelect  # opcjonalnie
    )

    def save(self, commit=True):
        instance = super().save(commit=False)

        selected = self.cleaned_data["correct_answer"]

        mapping = {
            "A": instance.answer_a,
            "B": instance.answer_b,
            "C": instance.answer_c,
            "D": instance.answer_d,
        }

        instance.correct_answer = mapping[selected]

        if commit:
            instance.save()

        return instance

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

    def __init__(self, *args, flashcard=None, **kwargs):
        super().__init__(*args, **kwargs)
        if flashcard:
            texts = list(
                flashcard.answers.order_by("pk").values_list("text", flat=True)
            )
            choices = [(t, t) for t in texts]

            # Shuffle only on initial display (GET). Keep stable order on POST.
            if not self.is_bound:
                random.shuffle(choices)

            self.fields["selected_answer"].choices = choices
