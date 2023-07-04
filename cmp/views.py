from django.shortcuts import render
from django.views import generic
from django.urls import reverse_lazy

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
import json

from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required, permission_required

from .models import Proveedor, ComprasEnc, CompraDet
from cmp.forms import ProveedorForm

from index.views import sinprivilegios

class ProveedorView(sinprivilegios, generic.ListView):
    model = Proveedor
    template_name = "cmp/proveedor_list.html"
    context_object_name = "obj"
    permission_required="cmp.view_proveedor"

class ProveedorNew(SuccessMessageMixin, sinprivilegios, generic.CreateView):
    permission_required = "cmp.add_proveedor"
    model = Proveedor
    template_name = "cmp/proveedor_form.html"
    context_object_name = "obj"
    form_class=ProveedorForm
    success_url=reverse_lazy("cmp:proveedor_list")

    def form_valid(self, form):
        form.instance.uc = self.request.user
        print(self.request.user.id)
        return super().form_valid(form)

class ProveedorEdit(SuccessMessageMixin, sinprivilegios, generic.UpdateView):
    permission_required = "cmp.change_proveedor"
    model=Proveedor
    template_name="cmp/proveedor_form.html"
    context_object_name="obj"
    form_class=ProveedorForm
    success_url=reverse_lazy("cmp:proveedor_list")

    def form_valid(self, form):
        form.instance.um = self.request.user.id
        print(self.request.user.id)
        return super().form_valid(form)

@login_required(login_url='/login/')
@permission_required('cmp.change_proveedor', login_url='index:sin_privilegios')
def proveedorInactivar(request,id):
    template_name="cmp/inactivar_prv.html"
    contexto={}
    prv = Proveedor.objects.filter(pk=id).first()

    if not prv:
        return HttpResponse('Proveedor no existe ' + str(id))
    
    if request.method == 'GET':
        contexto={'obj':prv}
    
    if request.method == 'POST':
        prv.estado=False
        prv.save()
        contexto={'obj':'OK'}
        return HttpResponse('Proveedor Inactivado')

    return render(request,template_name,contexto)

class ComprasView(sinprivilegios, generic.ListView):
    model = ComprasEnc
    template_name = "cmp/compras_list.html"
    context_object_name = "obj"
    permission_required="cmp.view_comprasenc"
