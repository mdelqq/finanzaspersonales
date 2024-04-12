from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Concept, Transaction, Categoria, ConsejoFinanzas

class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)

class ConsejoFinanzasAdmin(admin.ModelAdmin):
    list_display = ('consejo', 'fecha_creacion')
    search_fields = ('consejo',)
    list_filter = ('categorias', 'fecha_creacion')
    filter_horizontal = ('categorias',)

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = [
        "id",
        "email",
        "username",
        "numero_de_telefono",
        "direccion",
        "fecha_de_nacimiento",
        "imagen_de_perfil",
        "genero",
        "is_staff",
        "is_active",
    ]
    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("direccion","imagen_de_perfil",)}),
        ('Categories', {'fields': ('categorias_preferidas',)}),)
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {"fields": ("direccion", "imagen_de_perfil", 'categorias_preferidas',)}),)
    filter_horizontal = ('categorias_preferidas',)
    search_fields = ('username', 'email')
    ordering = ('username',)

class ConceptAdmin(admin.ModelAdmin):
    list_display = ('id','nombre', 'user', 'detalle', 'tipo')
    search_fields = ['id','nombre', 'user', 'detalle', 'tipo']
    list_filter = ['id','nombre', 'user', 'tipo']

class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id','nombre', 'user', 'fecha', 'concepto', 'cantidad']
    search_fields = ['id','nombre', 'user', 'concepto']
    list_filter = ['id','nombre', 'user', 'concepto']
    list_editable = ['concepto', 'cantidad']

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Concept, ConceptAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(ConsejoFinanzas, ConsejoFinanzasAdmin)