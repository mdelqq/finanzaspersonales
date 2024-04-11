from django.contrib.auth.forms import UserCreationForm, UserChangeForm, forms
from .models import CustomUser, Transaction, Concept, Categoria
from django.contrib.admin.widgets import FilteredSelectMultiple

class CustomUserCreationForm(UserCreationForm):
    categorias_preferidas = forms.ModelMultipleChoiceField(
        queryset=Categoria.objects.all(),
        widget=FilteredSelectMultiple("Categorías Preferidas", is_stacked=False),
        required=False,
        label='Categorías Preferidas'
    )

    class Meta(UserCreationForm):
        model = CustomUser
        numero_de_telefono = forms.CharField(label="Número de teléfono")
        direccion = forms.EmailField(label="Dirección")
        fields = (
            "username",
            "email",
            "numero_de_telefono",
            "direccion",
            "fecha_de_nacimiento",
            "imagen_de_perfil",
            "genero",
            'categorias_preferidas',
        )
        widgets = {
            'genero': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['categorias_preferidas'].help_text = 'Seleccione las categorías de su interés.'
        
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

class CustomUserChangeForm(UserChangeForm):
    remove_image = forms.BooleanField(required=False, label='Eliminar imagen de perfil')
    categorias_preferidas = forms.ModelMultipleChoiceField(
        queryset=Categoria.objects.all(),
        widget=FilteredSelectMultiple("Categorías Preferidas", is_stacked=False),
        required=False,
        label='Categorías Preferidas'
    )

    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
            "numero_de_telefono",
            "direccion",
            "fecha_de_nacimiento",
            "imagen_de_perfil",
            "genero",
            'categorias_preferidas',
        )
        widgets = {
            'genero': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['categorias_preferidas'].help_text = 'Seleccione las categorías de su interés.'
        
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['nombre', 'concepto', 'cantidad']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'concepto': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'required': True, 'step': '0.01'}),
        }
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(TransactionForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['concepto'].queryset = Concept.objects.filter(user=user)

class ConceptForm(forms.ModelForm):
    class Meta:
        model = Concept
        fields = ['nombre', 'detalle', 'tipo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'detalle': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'tipo': forms.Select(attrs={'class': 'form-control', 'required': True}),
        }
