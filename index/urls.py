from django.urls import path
from django.contrib.auth import views as auth_views

from index.views import Home, sinpermisos

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('login/',auth_views.LoginView.as_view(template_name='bases/login.html'),name='login'),
    path('logout/',auth_views.LogoutView.as_view(template_name='bases/login.html'),name='logout'),
    path('sin_privilegios/',sinpermisos.as_view(),name='sin_privilegios'),
]