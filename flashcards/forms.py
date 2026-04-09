from django import forms
from flashcards.models import Flashcard, Deck


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
            "answer_a",
            "answer_b",
            "answer_c",
            "answer_d",
            "correct_answer",
            "deck",
        ]


class FlashcardDeckForm(FlashcardForm):
    class Meta:
        model = Flashcard
        fields = [
            "question",
            "answer_a",
            "answer_b",
            "answer_c",
            "answer_d",
            "correct_answer",
        ]


class DeckForm(forms.ModelForm):
    class Meta:
        model = Deck
        fields = [
            "name",
        ]
