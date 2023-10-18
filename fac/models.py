from django.db import models

from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError

from index.models import ClaseModelo, ClaseModelo2
from inv.models import Producto

class Cliente(ClaseModelo):
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    nit = models.CharField(max_length=20, null=True, blank=True)
    direccion = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    celular = models.CharField(max_length=20, null=True, blank=True)


    def __str__(self):
        return '{} {}'.format(self.apellidos, self.nombres)
    
    def save (self):
        self.nombres = self.nombres.upper()
        self.apellidos = self.apellidos.upper()
        super(Cliente, self).save()

    class Meta:
        verbose_name_plural = "Clientes"

class FacturaEnc(ClaseModelo2):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    nit_factura = models.CharField(max_length=30,null=True)
    nombre_factura = models.CharField(max_length=300,null=True)
    direccion_factura = models.CharField(max_length=300,null=True)
    serie_factura = models.CharField(max_length=50,null=True)
    numero_factura = models.CharField(max_length=50,null=True)
    numero_interno = models.CharField(max_length=50,null=True)
    numero_autorizacion = models.CharField(max_length=100,null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    sub_total=models.FloatField(default=0)
    descuento=models.FloatField(default=0)
    total=models.FloatField(default=0)
    estado_fel = models.CharField(max_length=5,null=True)

    def __str__(self):
        return '{}'.format(self.id)

    def save(self):
        self.total = self.sub_total - self.descuento
        super(FacturaEnc,self).save()

    class Meta:
        verbose_name_plural = "Encabezado Facturas"
        verbose_name="Encabezado Factura"
        permissions = [
            ('del_facturaenc', 'permisos de admin de caja')
        ]
    

class FacturaDet(ClaseModelo2):
    factura = models.ForeignKey(FacturaEnc,on_delete=models.CASCADE)
    producto=models.ForeignKey(Producto,on_delete=models.CASCADE)
    cantidad=models.BigIntegerField(default=0)
    precio=models.FloatField(default=0)
    sub_total=models.FloatField(default=0)
    descuento=models.FloatField(default=0)
    total=models.FloatField(default=0)

    def __str__(self):
        return '{}'.format(self.producto)

    def save(self):
        self.sub_total = float(float(int(self.cantidad)) * float(self.precio))
        self.total = self.sub_total - float(self.descuento)
        super(FacturaDet, self).save()
    
    class Meta:
        verbose_name_plural = "Detalles Facturas"
        verbose_name="Detalle Factura"
        permissions = [
            ('del_facturadet', 'permisos de admin de caja')
        ]

@receiver(post_save, sender=FacturaDet)
def detalle_fac_guardar(sender,instance,**kwargs):
    factura_id = instance.factura.id
    producto_id = instance.producto.id

    enc = FacturaEnc.objects.get(pk=factura_id)
    if enc:
        sub_total = FacturaDet.objects \
            .filter(factura=factura_id) \
            .aggregate(sub_total=Sum('sub_total')) \
            .get('sub_total',0.00)
        
        descuento = FacturaDet.objects \
            .filter(factura=factura_id) \
            .aggregate(descuento=Sum('descuento')) \
            .get('descuento',0.00)
        
        enc.sub_total = sub_total
        enc.descuento = descuento
        enc.save()

    prod=Producto.objects.filter(pk=producto_id).first()
    if prod:
        cantidad = int(prod.existencia) - int(instance.cantidad)
        prod.existencia = cantidad
        prod.save()