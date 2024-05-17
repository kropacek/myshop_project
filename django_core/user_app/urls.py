from django.urls import path
from django.utils.translation import gettext_lazy as _

from .views import login_view, registration_view, profile_view, edit_view

app_name = 'user_app'


urlpatterns = [
    path(_('login/'), login_view, name='login_view'),
    path(_('registration/'), registration_view, name='registration_view'),
    path(_('profile/'), profile_view, name='profile_view'),
    path(_('edit/'), edit_view, name='edit_view'),
    path(_('logout'), login_view, name='logout_view1'),
]