from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.shortcuts import render 

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views import generic

class sinprivilegios(LoginRequiredMixin, PermissionRequiredMixin):
    login_url = 'base:login'
    raise_exception=False
    redirect_field_name="redirecto_to"

    def handle_no_permission(self):
        from django.contrib.auth.models import AnonymousUser
        if not self.request.user==AnonymousUser():
            self.login_url='index:sin_privilegios'
        return HttpResponseRedirect(reverse_lazy(self.login_url))

class Home(LoginRequiredMixin, generic.TemplateView):
    template_name = 'bases/home.html'
    login_url='index:login'

class sinpermisos(LoginRequiredMixin, generic.TemplateView):
    login_url = "base:login"
    template_name="bases/sinpermisos.html"