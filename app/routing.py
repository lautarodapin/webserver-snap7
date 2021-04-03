from django.urls import re_path
from .consumers import DatoProcesadoConsumer, DatosConsumer
websocket_urlpatterns = [
    re_path("^ws/$", DatosConsumer.as_asgi()),
    re_path("^ws/dato-procesado/$", DatoProcesadoConsumer.as_asgi()),
]