import re
from typing import OrderedDict
from rest_framework import serializers
from .models import Dato, DatoProcesado, Fila, Plc, Area
import json
class PlcSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plc
        fields = ["id", "ip", "rack", "slot", "port", "nombre", "areas"]
        depth = 6

    def to_representation(self, instance: Plc):
        data = super().to_representation(instance)
        data["areas"] = AreaSerializer(instance=instance.areas.all(), many=True).data if instance.areas.exists() else []
        return data
class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ["id", "created_at", "mod_at", "nombre", "area", "numero", "offset", "plc", "tag", "filas"]

    def to_representation(self, instance: Area) -> OrderedDict:
        data = super().to_representation(instance)
        data["filas"] = FilaSerializer(instance=instance.filas.all(), many=True).data if instance.filas.exists() else []
        return data

class FilaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fila
        fields = ["id", "area", "name", "byte", "bit", "tipo_dato"]


class DatoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dato
        fields = ["id", "created_at", "mod_at", "dato", "area"]

    def to_representation(self, instance: Dato) -> OrderedDict:
        data = super().to_representation(instance)
        data["area"] = AreaSerializer(instance=instance.area).data
        # data["dato"] = list(instance.dato)
        return data

        # TODO javascript Uint8Array.from(atob(response.results[0].dato), c => c.charCodeAt(0))


class DatoProcesadoSerializer(serializers.ModelSerializer):
    dato = serializers.SerializerMethodField()
    class Meta:
        model = DatoProcesado
        fields = [
            "id",
            "name",
            "date",
            "dato",
            "area",
            "fila",
            "raw_dato",
        ]
        depth = 0
        
    def get_dato(self, obj:DatoProcesado):
        return obj.value