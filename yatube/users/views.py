from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.shortcuts import render
from .forms import CreationForm, ChangePasswordForm


class SignUp(CreateView):
    form_class = CreationForm
    template_name = 'users/signup.html'
    success_url = reverse_lazy('posts:index')


class PasswordChangeView(CreateView):
    form_class = ChangePasswordForm
    template_name = 'users/password_change_form.html'
    success_url = reverse_lazy('posts:change_pass_done')


def success_pass_change(request):
    template = 'users/password_change_done.html'
    return render(request, template)
