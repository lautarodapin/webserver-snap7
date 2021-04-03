from typing import OrderedDict
from rest_framework import serializers
from .models import Dato, DatoProcesado, Fila, Plc, Area
import json
class PlcSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plc
        fields = ["id", "ip", "rack", "slot", "port", "nombre"]


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ["id", "created_at", "mod_at", "nombre", "area", "numero", "offset", "plc", "tag", "filas"]

    def to_representation(self, instance: Area) -> OrderedDict:
        response = super().to_representation(instance)
        response["plc"] = PlcSerializer(instance=instance.plc).data
        response["filas"] = []
        if instance.filas.exists():
            response["filas"] = FilaSerializer(instance=instance.filas.all(), many=True).data
        return response

class FilaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fila
        fields = ["id", "area", "name", "byte", "bit", "tipo_dato"]


class DatoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dato
        fields = ["id", "created_at", "mod_at", "dato", "area"]

    def to_representation(self, instance: Dato) -> OrderedDict:
        response = super().to_representation(instance)
        response["area"] = AreaSerializer(instance=instance.area).data
        # response["dato"] = list(instance.dato)
        return response

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
            "created_at",
            "area",
            "fila",
            "raw_dato",
        ]
        depth = 2
    def get_dato(self, obj:DatoProcesado):
        return obj.value