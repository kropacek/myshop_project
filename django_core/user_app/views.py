from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from django.views import View

from .forms import LoginForm, RegistrationForm, EditForm, PasswordResetForm
from .tasks import reset_password
from .models import CustomUser


def login_view(request):
    try:
        if request.user.email:
            return redirect('user_app:profile_view')
    except AttributeError:
        pass

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,
                                email=cd['email'],
                                password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, _('Authenticated successfully'))
                    return redirect('user_app:profile_view')
                else:
                    messages.warning(request, _('Disabled account'))
            else:
                messages.error(request, _('Invalid login'))

    else:
        form = LoginForm()

    context = {
        'form': form,
    }

    return render(request, 'user/login.html', context=context)


def registration_view(request):
    if request.method == 'POST':
        user_form = RegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password1'])
            new_user.save()

            login(request, new_user)

            messages.success(request, _('Profile created successfully'))

            return redirect('user_app:profile_view')

        messages.error(request, _('Error creating profile'))
    else:
        user_form = RegistrationForm()

    context = {
        'user_form': user_form,
    }

    return render(request, 'user/registration.html', context=context)


@login_required()
def profile_view(request):
    user = request.user

    context = {
        'user': user,
    }

    return render(request, 'user/profile.html', context=context)


@login_required()
def edit_view(request):
    if request.method == "POST":
        user_form = EditForm(instance=request.user,
                             data=request.POST)

        if user_form.is_valid():
            user_form.save()

            messages.success(request, _('Profile updated successfully'))

            return redirect('user_app:profile_view')
        else:
            messages.error(request, _('Error updating your profile'))
    else:
        user_form = EditForm(instance=request.user)

    context = {
        'user_form': user_form,
    }

    return render(request, 'user/edit.html', context=context)


@login_required()
def logout_view(request):
    logout(request)
    return redirect('user_app:login_view')


class PasswordResetView(View):

    def get(self, request):
        form = PasswordResetForm()

        context = {
            'form': form
        }

        return render(request, 'user/password-reset.html', context=context)

    def post(self, request):
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain

            user = CustomUser.objects.get(email__iexact=email)

            context = {
                "email": email,
                "domain": domain,
                "site_name": site_name,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": default_token_generator.make_token(user),
                "protocol": "http"
            }

            reset_password.delay(context=context)
            return render(request, 'user/password-reset-done.html')

        form = PasswordResetForm()

        context = {
            'form': form
        }

        return render(request, 'user/password-reset.html', context=context)