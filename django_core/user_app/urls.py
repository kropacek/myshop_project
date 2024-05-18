from django.contrib.auth.views import PasswordChangeDoneView, PasswordChangeView, \
    PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import path, reverse_lazy
from django.utils.translation import gettext_lazy as _

from .views import login_view, registration_view, profile_view, edit_view, logout_view, PasswordResetView
from .forms import CustomPasswordChangeForm


app_name = 'user_app'

urlpatterns = [
    path(_('login/'), login_view, name='login_view'),
    path(_('registration/'), registration_view, name='registration_view'),
    path(_('profile/'), profile_view, name='profile_view'),
    path(_('edit/'), edit_view, name='edit_view'),
    path(_('logout'), logout_view, name='logout_view'),

    # url-адреса смены пароля
    path('password-change/',
         PasswordChangeView.as_view(template_name='user/password-change.html',
                                    form_class=CustomPasswordChangeForm,
                                    success_url=reverse_lazy('user_app:password_change_done')),
         name='password_change'),
    path('password-change/done/',
         PasswordChangeDoneView.as_view(template_name='user/password-change-done.html'),
         name='password_change_done'),

    # url-адреса сброса пароля
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/',
         PasswordResetDoneView.as_view(template_name='user/password-reset-done.html'),
         name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(template_name='user/password-reset-token.html',
                                          success_url=reverse_lazy('user_app:password_reset_complete')),
         name='password_reset_confirm'),
    path('password-reset/complete/',
         PasswordResetCompleteView.as_view(template_name='user/password-reset-complete.html'),
         name='password_reset_complete'),
]