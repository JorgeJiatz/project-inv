from django.db import models

from index.models import ClaseModelo

class Cliente(ClaseModelo):
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    celular = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return '{} {}'.format(self.apellidos, self.nombres)
    
    def save (self):
        self.nombres = self.nombres.upper()
        self.apellidos = self.apellidos.upper()
        super(Cliente, self).save()

    class Meta:
        verbose_name_plural = "Clientes"
