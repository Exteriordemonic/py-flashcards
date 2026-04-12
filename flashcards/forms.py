import random

from django import forms
from django.forms import formset_factory


from flashcards.models import Flashcard, Answer


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = [
            "is_correct",
            "text",
        ]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # Formset rows may be left blank; we only persist rows with non-empty text in the view.
        self.fields["text"].required = False


AnswerFormSet = formset_factory(AnswerForm, extra=1)


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
