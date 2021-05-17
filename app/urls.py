from rest_framework import urlpatterns
from rest_framework.routers import DefaultRouter
from app.views import (
    DatoProcesadoViewset, DatoViewset, FilaViewset, PlcViewset, AreaViewset,
    DatoPreProcesadoViewset,
    )

router = DefaultRouter()
router.register('datos', DatoViewset, basename='dato')
router.register('datos-procesados', DatoProcesadoViewset, basename='dato-procesado')
router.register('plcs', PlcViewset, basename='plc')
router.register('filas', FilaViewset, basename='fila')
router.register('areas', AreaViewset, basename='area')
router.register('datos-pre-procesados', DatoPreProcesadoViewset, basename="dato-pre-procesado")

urlpatterns = router.urls