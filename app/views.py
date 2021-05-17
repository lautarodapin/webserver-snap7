from typing import List
from django.db.models import query
from django.shortcuts import render
from django.http import StreamingHttpResponse
from rest_framework import viewsets
from rest_framework.mixins import ListModelMixin
from rest_framework.decorators import action
from rest_framework.response import Response
import time
from django.contrib.auth.models import User
import json
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import (
    ChartDatoProcesadoSerializer, Dato, DatoSerializer, 
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

    @action(detail=False, methods=["get"])
    def filter_filas(self, request):
        filas : List[int] = map(int, request.GET.get("filas").split(","))
        queryset = self.get_queryset().filter(fila_id__in=filas)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    
    @action(detail=False, methods=["get"])
    def datos_procesados(self, request):
        filas : List[int] = map(int, request.GET.get("filas").split(","))
        queryset = self.get_queryset()\
            .filter(fila_id__in=filas)\
            .values("dato", "date", "fila", "name")
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ChartDatoProcesadoSerializer(page, many=True)
            # serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            response = Response(serializer.data)

        return response