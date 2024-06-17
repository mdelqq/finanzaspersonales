import os
import django
import random
from datetime import timedelta
from django.utils import timezone

# Asegúrate de que el nombre aquí corresponda al nombre correcto de tu proyecto Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mdelqq.settings')
django.setup()

from gecopf.models import CustomUser, Concept, Transaction

def random_date():
    end_date = timezone.now()
    start_date = end_date - timedelta(days=365)
    return start_date + timedelta(days=random.randint(0, 365))

# Crear una instancia de CustomUser (si no existe)
user, created = CustomUser.objects.get_or_create(
    username='familia_smith',
    defaults={
        'email': 'familia_smith@example.com',
        'first_name': 'Familia',
        'last_name': 'Smith',
    }
)

# Establecer la contraseña para el usuario
if created:
    user.set_password('familia_password')  # Aquí puedes cambiar la contraseña según tus necesidades
    user.save()
else:
    user.set_password('familia_password')
    user.save()

concept_types = {
    'Ingreso': ['Salario', 'Venta de artículos', 'Intereses bancarios', 'Otros ingresos'],
    'Gasto': ['Alquiler', 'Comida', 'Transporte', 'Ropa', 'Entretenimiento', 'Educación', 'Salud'],
    'Deuda': ['Pago de hipoteca', 'Pago de préstamo'],
    'Ahorro': ['Cuenta de ahorros', 'Inversiones']
}

def generate_amount(concept_type):
    if concept_type == 'Ingreso':
        return round(random.uniform(100, 5000), 2)
    elif concept_type == 'Gasto':
        return round(random.uniform(10, 2000), 2)
    elif concept_type == 'Deuda':
        return round(random.uniform(50, 1500), 2)
    elif concept_type == 'Ahorro':
        return round(random.uniform(50, 1000), 2)

for concept_type, names in concept_types.items():
    for name in names:
        Concept.objects.get_or_create(
            nombre=name,
            user=user,
            tipo=concept_type,
            defaults={
                'detalle': f'{name} relacionado con {concept_type.lower()}'
            }
        )

concepts = Concept.objects.filter(user=user)
for _ in range(1000):
    concept = random.choice(concepts)
    transaction_date = random_date()
    Transaction.objects.create(
        nombre=f'Transacción de {concept.nombre}',
        user=user,
        concepto=concept,
        fecha=transaction_date,
        cantidad=generate_amount(concept.tipo)
    )

print("Datos insertados correctamente")

from gecopf.models import Categoria, ConsejoFinanzas

# Categorías de consejos y sus descripciones
categorias = [
    ("Ahorro", "Consejos relacionados con el ahorro."),
    ("Inversiones", "Consejos relacionados con las inversiones."),
    ("Presupuesto", "Consejos relacionados con la elaboración y seguimiento de presupuestos."),
    ("Deudas", "Consejos relacionados con la gestión y reducción de deudas."),
    ("Educación Financiera", "Consejos relacionados con la educación financiera y la toma de decisiones."),
    ("Planificación para la jubilación", "Consejos relacionados con la planificación financiera para la jubilación."),
    ("Seguro y protección financiera", "Consejos relacionados con seguros y protección financiera."),
    ("Gastos inteligentes", "Consejos para realizar gastos inteligentes y eficientes."),
    ("Generación de ingresos adicionales", "Consejos para generar ingresos adicionales fuera del trabajo principal."),
    ("Reducción de costos", "Consejos para reducir costos y gastos innecesarios."),
]

# Crear categorías y consejos
for nombre, descripcion in categorias:
    # Crear la categoría
    categoria, _ = Categoria.objects.get_or_create(nombre=nombre, descripcion=descripcion)
    print(f"Categoría creada: {categoria}")

    # Consejos para cada categoría
    consejos = []
    if nombre == "Ahorro":
        consejos = [
            "Automatiza tus ahorros mensuales.",
            "Establece metas de ahorro realistas y alcanzables.",
            "Busca cuentas de ahorro con tasas de interés competitivas.",
            "Reduce tus gastos innecesarios para aumentar tu capacidad de ahorro.",
            "Considera invertir parte de tus ahorros en productos financieros con rendimientos atractivos.",
            "Crea un fondo de emergencia para cubrir gastos inesperados.",
            "Compra productos de segunda mano en lugar de nuevos para ahorrar dinero.",
            "Cocina en casa en lugar de comer fuera para reducir tus gastos.",
            "Evita las compras impulsivas y reflexiona antes de realizar una compra importante.",
            "Revisa tus facturas regularmente para identificar posibles errores o cargos innecesarios.",
        ]
    elif nombre == "Inversiones":
        consejos = [
            "Diversifica tus inversiones para reducir el riesgo.",
            "Realiza investigaciones exhaustivas antes de invertir en un producto financiero.",
            "Consulta a un asesor financiero para recibir orientación sobre tus inversiones.",
            "Mantén un horizonte de inversión a largo plazo para maximizar tus retornos.",
            "Reinvierte tus ganancias para acelerar el crecimiento de tu cartera de inversiones.",
            "No te dejes llevar por las emociones al tomar decisiones de inversión.",
            "Comprende tus objetivos financieros y selecciona las inversiones que mejor se adapten a ellos.",
            "No inviertas en productos financieros que no entiendas completamente.",
            "Aprovecha las cuentas de jubilación y los planes de inversión fiscalmente eficientes.",
            "Ahorra e invierte regularmente para aprovechar el poder del interés compuesto.",
        ]
    elif nombre == "Presupuesto":
        consejos = [
            "Crea un presupuesto detallado que incluya todos tus ingresos y gastos.",
            "Prioriza tus gastos y asigna fondos a las necesidades básicas primero.",
            "Haz un seguimiento de tus gastos diarios para identificar áreas donde puedes reducir costos.",
            "Revisa tu presupuesto regularmente y haz ajustes según sea necesario.",
            "Busca formas de aumentar tus ingresos, como buscar trabajos adicionales o negociar un aumento salarial.",
            "Establece límites de gastos para categorías específicas y sé disciplinado al cumplirlos.",
            "Considera utilizar herramientas de presupuesto en línea o aplicaciones móviles para facilitar el seguimiento de tus finanzas.",
            "Incluye un fondo de emergencia en tu presupuesto para cubrir gastos imprevistos.",
            "Evita tomar decisiones financieras impulsivas y tómate el tiempo para considerar las opciones disponibles.",
            "Busca oportunidades de ahorro, como descuentos, cupones o programas de recompensas.",
        ]
    elif nombre == "Deudas":
        consejos = [
            "Haz un inventario detallado de tus deudas, incluidos saldos pendientes, tasas de interés y plazos de pago.",
            "Prioriza el pago de deudas con tasas de interés más altas para minimizar los costos financieros.",
            "Considera consolidar tus deudas en un solo préstamo con una tasa de interés más baja si es posible.",
            "Negocia con tus acreedores para establecer planes de pago que sean más manejables para ti.",
            "Evita contraer nuevas deudas a menos que sea absolutamente necesario.",
            "Busca formas de aumentar tus ingresos para acelerar el proceso de pago de deudas.",
            "Busca asesoramiento financiero si estás luchando por manejar tus deudas de manera efectiva.",
            "Celebra tus logros a medida que pagas tus deudas, incluso si son pequeños hitos.",
            "Establece metas financieras claras y trabaja hacia ellas de manera constante.",
            "Mantén una actitud positiva y enfócate en el progreso que estás haciendo para liberarte de la deuda.",
        ]
    elif nombre == "Educación Financiera":
        consejos = [
            "Invierte tiempo en educarte sobre conceptos financieros básicos, como presupuesto, ahorro e inversión.",
            "Lee libros, blogs y artículos relacionados con finanzas personales para ampliar tu conocimiento.",
            "Participa en cursos en línea gratuitos o de bajo costo sobre educación financiera.",
            "Busca la orientación de un asesor financiero para obtener consejos personalizados sobre tus metas financieras.",
            "Habla con amigos y familiares sobre temas financieros para obtener diferentes perspectivas y consejos.",
            "Sigue a expertos financieros en redes sociales para recibir consejos y actualizaciones sobre tendencias financieras.",
            "Mantén un registro de tus gastos y revisa regularmente tus hábitos de gasto para identificar áreas de mejora.",
            "Fomenta una mentalidad de aprendizaje continuo en materia de finanzas para adaptarte a los cambios en el mercado.",
            "Aprende a analizar y comparar diferentes productos financieros, como cuentas de ahorro, inversiones y seguros.",
            "Establece metas financieras claras y desarrolla un plan para alcanzarlas, revisando y ajustando tu progreso regularmente.",
        ]
    elif nombre == "Planificación para la jubilación":
        consejos = [
            "Comienza a ahorrar para la jubilación lo antes posible para aprovechar al máximo el poder del interés compuesto.",
            "Conoce tus opciones de jubilación, como planes de pensiones, cuentas de jubilación individuales y planes 401(k).",
            "Calcula cuánto necesitas ahorrar para mantener tu estilo de vida deseado durante la jubilación.",
            "Considera diversificar tus inversiones para equilibrar el riesgo y el rendimiento a lo largo del tiempo.",
            "Consulta a un planificador financiero para ayudarte a diseñar un plan de jubilación personalizado.",
            "Revisa regularmente tu plan de jubilación y haz ajustes según cambien tus circunstancias personales y financieras.",
            "Aprovecha cualquier plan de ahorro para la jubilación ofrecido por tu empleador y contribuye lo máximo posible.",
            "Evita retirar fondos de tus cuentas de jubilación antes de la edad de jubilación, a menos que sea absolutamente necesario.",
            "Asegúrate de entender los beneficios de seguridad social y cómo afectarán tus ingresos durante la jubilación.",
            "Prepárate para la jubilación considerando factores como cuidado de la salud, vivienda y pasatiempos.",
        ]
    elif nombre == "Seguro y protección financiera":
        consejos = [
            "Evalúa tus necesidades de seguro, incluyendo seguro de vida, seguro de salud, seguro de automóvil y seguro de hogar.",
            "Comprende los diferentes tipos de pólizas de seguro y selecciona aquellas que se ajusten mejor a tus necesidades y presupuesto.",
            "Busca descuentos y ofertas especiales al comparar las tarifas de las compañías de seguros.",
            "Revisa tus pólizas de seguro regularmente para asegurarte de que sigan siendo adecuadas para tus circunstancias actuales.",
            "Considera la posibilidad de obtener un seguro de responsabilidad civil para protegerte contra demandas legales.",
            "Investiga sobre opciones de seguro de salud asequibles, especialmente si eres autónomo o no tienes cobertura a través de tu empleador.",
            "Asegura tus bienes más valiosos, como tu casa y tus vehículos, con suficiente cobertura de seguro.",
            "No subestimes la importancia del seguro de vida para proteger a tu familia y seres queridos en caso de tu fallecimiento.",
            "Mantén un fondo de emergencia en efectivo para cubrir gastos inesperados que no estén cubiertos por el seguro.",
            "Consulta a un agente de seguros de confianza para obtener asesoramiento profesional sobre tus necesidades de seguro.",
        ]
    elif nombre == "Gastos inteligentes":
        consejos = [
            "Crea un presupuesto mensual detallado que incluya todas tus fuentes de ingresos y gastos.",
            "Prioriza tus gastos según su importancia y necesidad, asignando más recursos a necesidades básicas y menos a deseos.",
            "Identifica áreas donde puedas reducir tus gastos mensuales, como comer fuera, entretenimiento y compras innecesarias.",
            "Compara precios y busca ofertas especiales al hacer compras grandes o planificar actividades.",
            "Utiliza cupones, descuentos y programas de fidelización para ahorrar dinero en tus compras habituales.",
            "Considera la posibilidad de comprar productos de segunda mano o reacondicionados en lugar de nuevos para ahorrar dinero.",
            "Planifica tus compras con anticipación y evita las compras impulsivas.",
            "Presupuesta un porcentaje de tus ingresos para gastos discrecionales y ajústalo según sea necesario.",
            "Aprovecha las oportunidades de ahorro, como ventas estacionales y promociones de liquidación.",
            "Sé consciente de tus hábitos de gasto y toma decisiones informadas sobre dónde y cómo gastar tu dinero.",
        ]
    elif nombre == "Generación de ingresos adicionales":
        consejos = [
            "Identifica tus habilidades y talentos únicos que puedas aprovechar para ganar dinero extra.",
            "Explora oportunidades de trabajo independiente o freelance en áreas como redacción, diseño gráfico, consultoría y tutoría.",
            "Considera la posibilidad de vender productos en línea a través de plataformas de comercio electrónico como Etsy, eBay o Amazon.",
            "Ofrece servicios de consultoría o asesoramiento en tu campo profesional para generar ingresos adicionales.",
            "Monetiza tus pasatiempos y pasiones, como la fotografía, la música o la cocina, creando contenido o productos para vender.",
            "Investiga oportunidades de trabajo remoto que te permitan ganar dinero desde la comodidad de tu hogar.",
            "Participa en encuestas en línea, paneles de opinión y programas de recompensas para ganar dinero extra.",
            "Considera alquilar una habitación adicional en tu casa a través de plataformas de alojamiento compartido como Airbnb.",
            "Aprovecha tus habilidades técnicas para ofrecer servicios de reparación, instalación o desarrollo web a clientes locales.",
            "No tengas miedo de probar cosas nuevas y explorar diferentes formas de generar ingresos adicionales.",
        ]
    elif nombre == "Reducción de costos":
        consejos = [
            "Revisa tus gastos mensuales y busca áreas donde puedas reducir costos, como suscripciones innecesarias o servicios de streaming que no utilizas.",
            "Compra productos genéricos en lugar de marcas de alta gama para ahorrar dinero en artículos de uso cotidiano.",
            "Compra productos a granel cuando sea posible para obtener descuentos por volumen y reducir los costos a largo plazo.",
            "Renegocia tus contratos de servicios, como Internet, teléfono y televisión por cable, para obtener tarifas más bajas.",
            "Apaga los dispositivos electrónicos y los electrodomésticos cuando no los estés utilizando para reducir los costos de energía.",
            "Reduce tus gastos de entretenimiento al optar por actividades gratuitas o de bajo costo, como caminatas al aire libre o noches de juegos en casa.",
            "Compara precios antes de realizar grandes compras y busca ofertas especiales, descuentos o promociones para obtener el mejor valor por tu dinero.",
            "Aprovecha los programas de recompensas y fidelización de las tiendas para obtener descuentos adicionales y reembolsos en tus compras habituales.",
            "Revisa tus facturas médicas y de seguros para identificar posibles errores o cargos innecesarios que puedan estar inflando tus costos.",
            "Considera opciones de transporte más económicas, como caminar, andar en bicicleta o utilizar el transporte público, en lugar de conducir o utilizar servicios de viaje compartido.",
        ]
    
    # Crear los consejos para la categoría actual
    for texto in consejos:
        consejo, _ = ConsejoFinanzas.objects.get_or_create(consejo=texto)
        consejo.categorias.set([categoria])
        print(f"Consejo creado para {categoria}: {texto}")

print("Categorías y consejos creados con éxito.")