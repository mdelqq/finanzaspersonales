from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(max_length=500, help_text="Ingrese una breve descripción de la categoría", blank=True, null=True)

    def __str__(self):
        return self.nombre

class ConsejoFinanzas(models.Model):
    consejo = models.TextField(max_length=500, help_text="Ingrese una breve descripción del consejo", blank=True, null=True)
    categorias = models.ManyToManyField(Categoria)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

class CustomUser(AbstractUser):
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('N', 'No Binario'),
    ]

    numero_de_telefono = models.CharField(max_length=15, null=True, blank=True, default='')
    direccion = models.CharField(max_length=255, null=True, blank=True, default='')
    fecha_de_nacimiento = models.DateField(null=True, blank=True)
    imagen_de_perfil = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES, null=True, blank=True, default='')
    categorias_preferidas = models.ManyToManyField(Categoria)
   
class Concept(models.Model):
    TIPO_CHOICES = [
        ('Ingreso', 'Ingreso'),
        ('Gasto', 'Gasto'),
        ('Deuda', 'Deuda'),
        ('Ahorro', 'Ahorro'),
    ]
    nombre = models.CharField(max_length=50, help_text="Ingrese el nombre del concepto", blank=False, null=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    detalle = models.TextField(max_length=500, help_text="Ingrese una breve descripción del concepto", blank=True, null=True)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, help_text="Ingrese el tipo del concepto", blank=False, null=False)

    def __str__(self):
        return self.nombre

class Transaction(models.Model):
    nombre = models.CharField(max_length=50, help_text="Ingrese el nombre de la transacción", blank=False, null=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    concepto = models.ForeignKey(Concept, on_delete=models.CASCADE, null=True)
    #fecha  = models.DateTimeField(auto_now=False, auto_now_add=True)
    fecha  = models.DateTimeField(default=timezone.now)
    
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Ingrese la cantidad en euros", blank=False, null=False)

    def __str__(self):
        return self.nombre
