from django.urls import path

from . import views
from .views import SignUpView, ProfileUpdateView

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    #path('profile/', views.profile, name='profile'),
    path('profile/', ProfileUpdateView.as_view(), name='profile'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('analisis/', views.analisis_datos, name='analisis'),
    path('acumulado/', views.analisis_datos_acum, name='acumulado'),
    path('resumen/', views.resumen_datos, name='resumen'),
    path('seleccionar_consejo_aleatorio/', views.seleccionar_consejo_aleatorio, name='seleccionar_consejo_aleatorio'),
    path('verificar_tendencias/', views.verificar_tendencias, name='verificar_tendencias'),
]