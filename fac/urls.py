from django.urls import path, include

from .views import ClienteView, ClienteEdit, ClienteNew, clienteInactivar

urlpatterns = [
    path('clientes/',ClienteView.as_view(), name="cliente_list"),
    path('clientes/new', ClienteNew.as_view(), name="cliente_new"),
    path('clientes/<int:pk>', ClienteEdit.as_view(), name="cliente_edit"),
    path('clientes/estado/<int:id>',clienteInactivar, name="cliente_inactivar"),
]