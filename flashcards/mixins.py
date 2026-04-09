from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect


class OwnerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return obj.owner == self.request.user

    def handle_no_permission(self):
        return redirect("flashcards:deck-list")


class CreatedByRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return obj.created_by == self.request.user

    def handle_no_permission(self):
        return redirect("flashcards:deck-list")
