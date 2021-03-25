from typing import OrderedDict
from rest_framework import serializers
from .models import Dato, Fila, Plc, Area

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
        return response