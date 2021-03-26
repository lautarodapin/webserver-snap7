from django.urls import re_path
from .consumers import DatosConsumer
websocket_urlpatterns = [
    re_path("^ws/$", DatosConsumer.as_asgi()),
]