from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import render, redirect

from .forms import RegisterForm


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        form = RegisterForm()

    return render(request, "registration/register.html", {"form": form})
