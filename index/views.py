from django.http import HttpResponseRedirect
from django.urls import reverse_lazy 
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.shortcuts import render
from datetime import datetime, timedelta

from pathlib import Path
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views import generic
from inv.models import Producto, Marca, SubCategoria
from cmp.models import Proveedor
from fac.models import Cliente, FacturaEnc

class sinprivilegios(LoginRequiredMixin, PermissionRequiredMixin):
    login_url = 'index:login'
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
    login_url = 'index:login'
    template_name="bases/sinpermisos.html"

#reset contraseña
class CustomPasswordResetView(PasswordResetView):
    template_name = 'bases/login_reset.html'
    email_template_name = 'bases/reset_email.html'  # Plantilla de correo electrónico personalizada
    success_url = '/reset_password_send/'

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'bases/reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'bases/reset_confirm.html'
    success_url = '/reset_password_complete/'  # URL de éxito para el restablecimiento de contraseña

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'bases/reset_complete.html'

@login_required(login_url='/login/')
def dashboard(request):
    total_productos = Producto.objects.count()
    cantidad_proveedores = Proveedor.objects.count()
    total_clientes = Cliente.objects.count()
    total_marca = Marca.objects.count()
    total_subcategoria = SubCategoria.objects.count()
    fecha_limite = datetime.now() - timedelta(days=30)
    total_fac = FacturaEnc.objects.filter(fecha__gte=fecha_limite).count()

    context = {
        'total_productos': total_productos,
        'cantidad_proveedores': cantidad_proveedores,
        'total_clientes': total_clientes,
        'total_marca': total_marca,
        'total_subcategoria':total_subcategoria,
        'total_fac': total_fac
    }

    return render(request,'bases/home.html',context)

