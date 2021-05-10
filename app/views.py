from django.db.models import query
from django.shortcuts import render
from django.http import StreamingHttpResponse
from rest_framework import viewsets
from rest_framework.mixins import ListModelMixin
import time
from django.contrib.auth.models import User
import json
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import (
    Dato, DatoSerializer, 
    DatoProcesado, DatoProcesadoSerializer,
    Plc, PlcSerializer,
    Fila, FilaSerializer,
    Area, AreaSerializer,
)

class PlcViewset(viewsets.ModelViewSet):
    queryset = Plc.objects.all()
    serializer_class = PlcSerializer

    
class FilaViewset(viewsets.ModelViewSet):
    queryset = Fila.objects.all()
    serializer_class = FilaSerializer


class AreaViewset(viewsets.ModelViewSet):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer

class DatoViewset(viewsets.ModelViewSet):
    queryset = Dato.objects.select_related("area",).prefetch_related("area", "area__filas")
    serializer_class = DatoSerializer


        
class DatoProcesadoViewset(viewsets.ModelViewSet):
    queryset = DatoProcesado.objects.all()
    serializer_class = DatoProcesadoSerializer
    # lookup_field = "fila_id"
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['fila__id', 'area__id', ]

    def get_queryset(self):
        queryset = super().get_queryset()
        filtered = self.request.GET.get("fila_id")
        if filtered:
            queryset = queryset.filter(fila_id=filtered)
        return queryset