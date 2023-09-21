from django.urls import path
from django.contrib.auth import views as auth_views

from index.views import Home, sinpermisos, CustomPasswordResetView, CustomPasswordResetConfirmView, CustomPasswordResetDoneView, CustomPasswordResetCompleteView, dashboard

urlpatterns = [
    #path('', Home.as_view(), name='home'),
    path('', dashboard, name='home'),
    path('login/',auth_views.LoginView.as_view(template_name='bases/login.html'), name='login'),
    path('logout/',auth_views.LogoutView.as_view(template_name='bases/login.html'), name='logout'),
    path('sin_privilegios/',sinpermisos.as_view(),name='sin_privilegios'),

    path('reset_password/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('reset_password_send/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset_password_complete/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),

]