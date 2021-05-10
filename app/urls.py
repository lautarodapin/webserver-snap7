from rest_framework import urlpatterns
from rest_framework.routers import DefaultRouter
from app.views import DatoProcesadoViewset, DatoViewset, FilaViewset, PlcViewset, AreaViewset

router = DefaultRouter()
router.register('datos', DatoViewset, basename='dato')
router.register('datos-procesados', DatoProcesadoViewset, basename='dato-procesado')
router.register('plcs', PlcViewset, basename='plc')
router.register('filas', FilaViewset, basename='fila')
router.register('areas', AreaViewset, basename='area')

urlpatterns = router.urls