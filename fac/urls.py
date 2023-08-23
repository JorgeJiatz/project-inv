from django.urls import path, include

from .views import ClienteView, ClienteEdit, ClienteNew, clienteInactivar, \
    FacturaView, facturas, ProductView, del_detalle_factura

urlpatterns = [
    path('clientes/',ClienteView.as_view(), name="cliente_list"),
    path('clientes/new',ClienteNew.as_view(), name="cliente_new"),
    path('clientes/<int:pk>',ClienteEdit.as_view(), name="cliente_edit"),
    path('clientes/estado/<int:id>',clienteInactivar, name="cliente_inactivar"),
    path('facturas/',FacturaView.as_view(), name="factura_list"), 
    path('facturas/new',facturas, name="factura_new"),
    path('facturas/edit/<int:id>',facturas, name="factura_edit"),
    path('facturas/buscar-product',ProductView.as_view(), name="fac_product"),
    path('facturas/del_detalle_factura/<int:id>',del_detalle_factura, name="del_detalle_factura")
]