import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import json, requests, pandas as pd, io, base64
import random

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomUserChangeForm, TransactionForm, ConceptForm
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from .models import CustomUser, Concept, Transaction, ConsejoFinanzas
from django.contrib import messages
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Sum

def index(request):
    noticias = obtener_noticias()
    return render(request, 'index.html', {'noticias': noticias, 'index': True})

@login_required
def home(request):
    #form = TransactionForm()
    form = TransactionForm(user=request.user)
    formCon = ConceptForm()
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == None:
            data = json.loads(request.body)
            action = data.get('action')
        if action == 'edit':
            edit_transaction(request, data)   
        elif action == 'delete':
            delete_transaction(request)
        elif action == 'newTransaction':
            create_transaction(request)
        elif action == 'newConcept':
            create_concept(request)
        return redirect('home')       
    else:
        form = TransactionForm(user=request.user)
        formCon = ConceptForm()
    
    transactions = Transaction.objects.filter(user=request.user).order_by('-fecha')
    concept_names = Concept.objects.filter(user=request.user).values_list('nombre', flat=True)

    transaction_data, totals = prepare_transaction_data(transactions, concept_names)

    # Calcular total general
    total_general = sum(totals.values())
    
    context = {
        'home': True,
        'transaction_data': transaction_data,
        'concept_names': concept_names,
        'totals': totals,
        'total_general': total_general,
        'form': form,
        'formCon': formCon,
    }
    
    return render(request, 'home.html', context)

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "signup.html"

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = 'profile.html'
    success_url = reverse_lazy('profile')
    def get_object(self):
        return self.request.user
    def form_valid(self, form):
        user = form.save(commit=False)     
        # Verifica si se ha marcado la casilla de eliminación de imagen
        if form.cleaned_data.get('remove_image'):
            if user.imagen_de_perfil:  # Verifica si hay una imagen de perfil para eliminar
                user.imagen_de_perfil.delete()  # Elimina la imagen de perfil
                user.imagen_de_perfil = None  # Asigna None al campo imagen_de_perfil      
        # Verifica si se ha cargado una nueva imagen de perfil
        elif self.request.FILES:
            user.imagen_de_perfil = self.request.FILES.get('imagen_de_perfil', None)      
        user.save()
        messages.success(self.request, 'Tu perfil ha sido actualizado exitosamente.')
        return super().form_valid(form)
    
def edit_transaction(request, data):
    transaction_id = data.get('transaction_id')
    name = data.get('name')
    concept = data.get('concept')
    amount = data.get('amount')
    try:
        transaction = Transaction.objects.get(pk=transaction_id, user=request.user)
        #transaction.id = transaction_id
        transaction.nombre = name
        #transaction.concepto = concept
        transaction.cantidad = amount
        #transaction.user = request.user
        transaction.save()
        messages.success(request, 'Transacción actualizada exitosamente.')
    except Transaction.DoesNotExist:
        messages.error(request, 'La transacción especificada no existe.')
    except Exception as e:
        print('Error al actualizar la transacción:', e)  # Imprime cualquier excepción que ocurra
        messages.error(request, 'Ocurrió un error al actualizar la transacción.')

def delete_transaction(request):
    transaction_id = request.POST.get('transaction_id')
    try:
        transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
        transaction.delete()
        messages.success(request, 'Transacción eliminada correctamente.')
    except Transaction.DoesNotExist:
        messages.error(request, 'La transacción no se ha eliminado. Contacte con su administrador.')

def create_transaction(request):
    form = TransactionForm(request.POST)
    if form.is_valid():
        try:
            new_transaction = form.save(commit=False)
            new_transaction.user = request.user
            new_transaction.save()
            messages.success(request, 'Transacción generada correctamente.')
        except Exception as e:
            messages.error(request, 'La transacción no se ha generado. Contacte con su administrador.')
    else:
        messages.error(request, 'La transacción no se ha generado. Contacte con su administrador.')

def create_concept(request):
    form = ConceptForm(request.POST)
    if form.is_valid():
        try:
            new_concept = form.save(commit=False)
            new_concept.user = request.user
            new_concept.save()
            messages.success(request, 'Concepto generado correctamente.')
        except Exception as e:
            messages.error(request, 'El concepto no se ha generado. Contacte con su administrador.')
    else:
        messages.error(request, 'El concepto no se ha generado. Contacte con su administrador.')

def prepare_transaction_data(transactions, concept_names):
    transaction_data = []
    totals = {concept_name: 0 for concept_name in concept_names}
    for transaction in transactions:
        row = {
            'id': transaction.id,
            'fecha': transaction.fecha,
            'nombre': transaction.nombre,
            'concepto': transaction.concepto,
            'cantidad': transaction.cantidad,
            'conceptos': {concept_name: 0 for concept_name in concept_names} 
        }
        if transaction.concepto:
            concept_name = transaction.concepto.nombre
            row['conceptos'][concept_name] = transaction.cantidad
            totals[concept_name] += transaction.cantidad
        transaction_data.append(row)
    return transaction_data, totals

def obtener_noticias():
    url = "https://newsapi.org/v2/everything"
    querystring = {"q": "finanzas", "language": "es", "apiKey": "c304f2dd91b94caf995d84e1ddc439a7"}
    response = requests.get(url, params=querystring)
    noticias = response.json().get('articles', [])
    return noticias

@login_required
def analisis_datos(request):
    usuario_actual = request.user
    fecha_limite = timezone.now() - timedelta(days=365)
    transacciones = Transaction.objects.filter(user=usuario_actual, fecha__gte=fecha_limite)

    if not transacciones.exists():
        return render(request, 'analisis.html', {'regresiones': {}, 'analisis': True, 'mensaje': 'No hay datos disponibles para análisis.'})
    
    transacciones_list = list(transacciones.values('fecha', 'cantidad', 'concepto__tipo'))
    if not transacciones_list:
        return render(request, 'analisis.html', {'regresiones': {}, 'analisis': True, 'mensaje': 'No hay datos disponibles después de la consulta.'})

    df = pd.DataFrame(list(transacciones.values('fecha', 'cantidad', 'concepto__tipo')))

    required_columns = {'fecha', 'cantidad', 'concepto__tipo'}
    if not required_columns.issubset(df.columns):
        return render(request, 'analisis.html', {'regresiones': {}, 'analisis': True, 'mensaje': f'Faltan datos necesarios para el análisis. Columnas presentes: {df.columns.tolist()}'})

    try:
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    except KeyError as e:
        return render(request, 'analisis.html', {'regresiones': {}, 'analisis': False, 'mensaje': f'Error al convertir la columna fecha: {str(e)}'})

    df = df.dropna(subset=['fecha'])
    df['mes'] = df['fecha'].dt.month
    df['año'] = df['fecha'].dt.year
    df['cantidad'] = pd.to_numeric(df['cantidad'])
    df = df.dropna(subset=['cantidad'])
    
    if df.empty:
        return render(request, 'analisis.html', {'regresiones': {}, 'analisis': True, 'mensaje': 'No hay datos válidos después de la limpieza.'})
    
    # Datos acumulados por tipo de concepto
    df_grouped = df.groupby(['año', 'mes', 'concepto__tipo'])['cantidad'].sum().reset_index()
    df_grouped['cantidad_acumulada'] = df_grouped.groupby('concepto__tipo')['cantidad'].cumsum()

    regresiones = {}
    for tipo_concepto in df_grouped['concepto__tipo'].unique():
        datos_tipo_concepto = df_grouped[df_grouped['concepto__tipo'] == tipo_concepto]
        regresor = LinearRegression()

        try:
            regresor.fit(datos_tipo_concepto[['mes']], datos_tipo_concepto['cantidad'])
            prevision = regresor.predict([[13]])[0]  # Previsión para el mes 13 (enero del siguiente año)
        except Exception as e:
            return render(request, 'analisis.html', {'regresiones': {}, 'analisis': True, 'mensaje': f'Error en el cálculo de regresión: {str(e)}'})
        
        regresiones[tipo_concepto] = {
            'pendiente': regresor.coef_[0],
            'intercepto': regresor.intercept_,
            'prevision': prevision,
            'grafica_base64': generar_grafica(datos_tipo_concepto, tipo_concepto)
        }

        # Generar la gráfica en un hilo separado
        #t = threading.Thread(target=generar_grafica, args=(datos_tipo_concepto, tipo_concepto))
        #t.start()

    # Renderizar la plantilla con los datos y la imagen base64
    return render(request, 'analisis.html', {'regresiones': regresiones, 'analisis': True})

    #return render(request, 'analisis_datos.html', {'regresiones': regresiones})

def generar_grafica(datos_tipo_concepto, tipo_concepto):
    plt.scatter(datos_tipo_concepto['mes'], datos_tipo_concepto['cantidad'], color='blue')
    plt.xlabel('Mes')
    plt.ylabel('Cantidad')
    plt.title(f'Gráfica de regresión para {tipo_concepto}')
    plt.grid(True)

    # Ajustar la regresión lineal
    regresor = LinearRegression()
    regresor.fit(datos_tipo_concepto[['mes']], datos_tipo_concepto['cantidad'])
    
    # Dibujar la línea de regresión
    x_values = np.array(range(1, 13))  # 12 meses
    y_values = regresor.predict(x_values.reshape(-1, 1))
    plt.plot(x_values, y_values, color='red')

    # Guardar la gráfica en un archivo de imagen
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    # Convertir la imagen a formato base64
    graph = base64.b64encode(image_png).decode()
    plt.close()
    return graph

    #with open(f'media/regresion_{tipo_concepto}.png', 'wb') as f:
        #f.write(image_png)

    # Guardar o mostrar la imagen según tus necesidades
    # En este caso, podrías guardar la imagen en el servidor o simplemente devolverla al cliente
    # Aquí un ejemplo de cómo guardar la imagen:
    # with open(f'media/regresion_{tipo_concepto}.png', 'wb') as f:
    #     f.write(image_png)
    # Luego, en el template, podrías mostrar la imagen usando la ruta media/regresion_tipo_de_concepto.png
    # O, puedes enviar la imagen como datos base64 a tu template y mostrarla directamente desde allí

@login_required
def analisis_datos_acum(request):
    usuario_actual = request.user
    fecha_limite = timezone.now() - timedelta(days=365)
    transacciones = Transaction.objects.filter(user=usuario_actual, fecha__gte=fecha_limite)

    if not transacciones.exists():
        return render(request, 'acumulado.html', {'regresiones': {}, 'analisis': True, 'mensaje': 'No hay datos disponibles para análisis.'})
    
    transacciones_list = list(transacciones.values('fecha', 'cantidad', 'concepto__tipo'))
    if not transacciones_list:
        return render(request, 'acumulado.html', {'regresiones': {}, 'analisis': True, 'mensaje': 'No hay datos disponibles después de la consulta.'})

    df = pd.DataFrame(list(transacciones.values('fecha', 'cantidad', 'concepto__tipo')))

    required_columns = {'fecha', 'cantidad', 'concepto__tipo'}
    if not required_columns.issubset(df.columns):
        return render(request, 'acumulado.html', {'regresiones': {}, 'analisis': True, 'mensaje': 'Faltan datos necesarios para el análisis.'})
    
    try:
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    except KeyError as e:
        return render(request, 'acumulado.html', {'regresiones': {}, 'analisis': False, 'mensaje': f'Error al convertir la columna fecha: {str(e)}'})

    df = df.dropna(subset=['fecha'])

    df['mes'] = df['fecha'].dt.month
    df['año'] = df['fecha'].dt.year
    df['cantidad'] = pd.to_numeric(df['cantidad'])
    df = df.dropna(subset=['cantidad'])

    if df.empty:
        return render(request, 'acumulado.html', {'regresiones': {}, 'analisis': True, 'mensaje': 'No hay datos válidos después de la limpieza.'})

    # Datos agrupados y acumulados por tipo de concepto
    df_grouped = df.groupby(['año', 'mes', 'concepto__tipo'])['cantidad'].sum().reset_index()
    df_grouped['cantidad_acumulada'] = df_grouped.groupby('concepto__tipo')['cantidad'].cumsum()

    regresiones = {}
    for tipo_concepto in df_grouped['concepto__tipo'].unique():
        datos_tipo_concepto = df_grouped[df_grouped['concepto__tipo'] == tipo_concepto]
        regresor = LinearRegression()

        try:
            regresor.fit(datos_tipo_concepto[['mes']], datos_tipo_concepto['cantidad_acumulada'])
            prevision = regresor.predict([[13]])[0]  # Previsión para el mes 13 (enero del siguiente año)
        except Exception as e:
            return render(request, 'acumulado.html', {'regresiones': {}, 'analisis': True, 'mensaje': f'Error en el cálculo de regresión: {str(e)}'})
        
        regresiones[tipo_concepto] = {
            'pendiente': regresor.coef_[0],
            'intercepto': regresor.intercept_,
            'prevision': prevision,
            'grafica_base64': generar_grafica_acum(datos_tipo_concepto, tipo_concepto, regresor)
        }

    return render(request, 'acumulado.html', {'regresiones': regresiones, 'analisis': True})

def generar_grafica_acum(datos_tipo_concepto, tipo_concepto, regresor):
    plt.figure(figsize=(10, 6))
    plt.scatter(datos_tipo_concepto['mes'], datos_tipo_concepto['cantidad_acumulada'], color='blue')
    plt.plot(datos_tipo_concepto['mes'], regresor.predict(datos_tipo_concepto[['mes']]), color='red', linewidth=2)
    plt.xlabel('Mes')
    plt.ylabel('Cantidad Acumulada')
    plt.title(f'Gráfica de regresión acumulada para {tipo_concepto}')
    plt.grid(True)

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    graph = base64.b64encode(image_png).decode()
    plt.close()
    return graph

@login_required
def resumen_datos(request):
    usuario_actual = request.user
    fecha_limite = timezone.now() - timedelta(days=365)
    transacciones = Transaction.objects.filter(user=usuario_actual, fecha__gte=fecha_limite)

    # Obtener los filtros de la solicitud GET
    año = request.GET.get('año')
    mes = request.GET.get('mes')

    if año:
        transacciones = transacciones.filter(fecha__year=año)
    if mes:
        transacciones = transacciones.filter(fecha__month=mes)
    
    if not transacciones.exists():
        return render(request, 'resumen.html', {
            'analisis': True,
            'grafica_base64': None,
            'totales': [],
            'año': año,
            'mes': mes,
            'años': list(range(datetime.now().year - 4, datetime.now().year + 1)),
            'meses': [
                (1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'),
                (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'),
                (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre')
            ],
            'mensaje': 'No hay datos disponibles para análisis.'
        })
    
    transacciones_list = list(transacciones.values('concepto__tipo', 'cantidad'))
    if not transacciones_list:
        return render(request, 'resumen.html', {
            'analisis': True,
            'grafica_base64': None,
            'totales': [],
            'año': año,
            'mes': mes,
            'años': list(range(datetime.now().year - 4, datetime.now().year + 1)),
            'meses': [
                (1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'),
                (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'),
                (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre')
            ],
            'mensaje': 'No hay datos disponibles después de la consulta.'
        })

    # Agrupar por concepto y calcular totales
    df = pd.DataFrame(transacciones_list)

    if 'cantidad' not in df.columns or 'concepto__tipo' not in df.columns:
        return render(request, 'resumen.html', {
            'analisis': True,
            'grafica_base64': None,
            'totales': [],
            'año': año,
            'mes': mes,
            'años': list(range(datetime.now().year - 4, datetime.now().year + 1)),
            'meses': [
                (1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'),
                (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'),
                (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre')
            ],
            'mensaje': 'Faltan datos necesarios para el análisis.'
        })

    df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce')
    df = df.dropna(subset=['cantidad'])

    if df.empty:
        return render(request, 'resumen.html', {
            'analisis': True,
            'grafica_base64': None,
            'totales': [],
            'año': año,
            'mes': mes,
            'años': list(range(datetime.now().year - 4, datetime.now().year + 1)),
            'meses': [
                (1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'),
                (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'),
                (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre')
            ],
            'mensaje': 'No hay datos válidos después de la limpieza.'
        })

    df_grouped = df.groupby('concepto__tipo')['cantidad'].sum().reset_index()
    totales = df_grouped.to_dict(orient='records')

    if not df_grouped.empty:
        fig, ax = plt.subplots()
        ax.pie(df_grouped['cantidad'], labels=df_grouped['concepto__tipo'], autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        plt.title('Distribución de Conceptos')

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        graph = base64.b64encode(image_png).decode()
        plt.close()
    else:
        graph = None

    años = list(range(datetime.now().year - 4, datetime.now().year + 1))
    meses = [
        (1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'),
        (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'),
        (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre')
    ]

    return render(request, 'resumen.html', {
        'analisis': True,
        'grafica_base64': graph,
        'totales': totales,
        'año': año,
        'mes': mes,
        'años': años,
        'meses': meses
    })

@login_required
def seleccionar_consejo_aleatorio(request):
    usuario = request.user
    categorias_preferidas = usuario.categorias_preferidas.all()
    consejos_disponibles = ConsejoFinanzas.objects.filter(categorias__in=categorias_preferidas).distinct()
    
    # Filtrar consejos que no se han mostrado en los últimos 10 minutos
    ahora = timezone.now()
    tiempo_limite = ahora - timezone.timedelta(minutes=10)
    consejos_mostrados = request.session.get('consejos_mostrados', [])
    consejos_disponibles = consejos_disponibles.exclude(id__in=consejos_mostrados).filter(fecha_creacion__lte=tiempo_limite)
    
    if consejos_disponibles.exists():
        consejo_aleatorio = random.choice(consejos_disponibles)
        # Agregar el consejo mostrado a la lista de consejos mostrados
        consejos_mostrados.append(consejo_aleatorio.id)
        request.session['consejos_mostrados'] = consejos_mostrados
        categoria = consejo_aleatorio.categorias.first().nombre
        consejo = consejo_aleatorio.consejo
    else:
        categoria = 'N/A'
        consejo = 'No hay consejos disponibles en este momento.'
    return JsonResponse({'categoria': categoria, 'consejo': consejo})

def detectar_incremento_ingresos(usuario, porcentaje=20):
    hoy = timezone.now()
    hace_un_mes = hoy - timedelta(days=30)
    
    ingresos_ultimo_mes = Transaction.objects.filter(
        user=usuario, concepto__tipo='Ingreso', fecha__range=[hace_un_mes, hoy]
    ).aggregate(total=Sum('cantidad'))['total'] or 0
    
    ingresos_mes_anterior = Transaction.objects.filter(
        user=usuario, concepto__tipo='Ingreso', fecha__range=[hace_un_mes - timedelta(days=30), hace_un_mes]
    ).aggregate(total=Sum('cantidad'))['total'] or 0

    if ingresos_mes_anterior > 0:
        incremento = ((ingresos_ultimo_mes - ingresos_mes_anterior) / ingresos_mes_anterior) * 100
        if incremento >= porcentaje:
            return True, incremento
    return False, 0

def detectar_gastos_excesivos(usuario, umbral=1000):
    hoy = timezone.now()
    hace_un_mes = hoy - timedelta(days=30)
    
    gastos_ultimo_mes = Transaction.objects.filter(
        user=usuario, concepto__tipo='Gasto', fecha__range=[hace_un_mes, hoy]
    ).aggregate(total=Sum('cantidad'))['total'] or 0
    
    if gastos_ultimo_mes > umbral:
        return True, gastos_ultimo_mes
    return False, 0

@login_required
def verificar_tendencias(request):
    usuario = request.user
    avisos = []
    
    incremento_ingresos, porcentaje = detectar_incremento_ingresos(usuario)
    if incremento_ingresos:
        avisos.append(f"¡Tus ingresos han aumentado un {porcentaje}% en el último mes!")

    gastos_excesivos, total_gastos = detectar_gastos_excesivos(usuario)
    if gastos_excesivos:
        avisos.append(f"¡Has gastado más de {total_gastos}€ en el último mes!")

    return JsonResponse({'avisos': avisos})