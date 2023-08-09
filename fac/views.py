from django.shortcuts import render
from django.views import generic

from index.views import sinprivilegios
from .models import Cliente

class ClienteView(sinprivilegios, generic.ListView):
    model = Cliente
    template_name = "fac/cliente_list.html"
    context_object_name = "obj"
    permission_required="cmp.view_cliente"
