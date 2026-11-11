"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from productos.views import IngredienteViewSet
from pedidos.views import (
    ClienteViewSet,
    PedidoViewSet,
    DetallePedidoViewSet,
    CotizacionViewSet
)
from despachos.views import DespachoViewSet
from inventario.views import MovimientoInventarioViewSet

router = DefaultRouter()

router.register('ingredientes', IngredienteViewSet)
router.register('clientes', ClienteViewSet)
router.register('pedidos', PedidoViewSet)
router.register('detalles-pedidos', DetallePedidoViewSet)
router.register('cotizaciones', CotizacionViewSet)
router.register('despachos', DespachoViewSet)
router.register('movimientos-inventario', MovimientoInventarioViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('', include('panel.urls')),
]
