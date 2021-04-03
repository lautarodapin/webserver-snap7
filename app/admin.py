from django.contrib import admin
from .models import *

@admin.register(Plc)
class PlcAdmin(admin.ModelAdmin):
    pass

@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    pass

@admin.register(Dato)
class DatoAdmin(admin.ModelAdmin):
    list_display = ["id", "area", "get_created_at", "dato", "procesado",]
    list_filter = ["procesado",]

    def get_created_at(self, obj: Dato):
        date: datetime = obj.created_at
        return date.strftime("%d-%m-%y %H:%M:%S")
    
    get_created_at.short_description = "Created"

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Fila)
class FilaAdmin(admin.ModelAdmin):
    list_display = ["id", "area", "name", "byte", "bit", "tipo_dato", "get_value"]

    def get_value(self, obj: Fila):
        return obj.read_value(obj.area.datos.first().dato)
    get_value.short_description = "Last value"


@admin.register(DatoProcesado)
class DatoProcesadoAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "get_date",
        "dato",
        "area",
        "fila",
        "raw_dato",
        "created_at",
        "mod_at",
    ]

    list_filter = ["area", "fila",]

    
    def get_date(self, obj: DatoProcesado):
        return obj.date.strftime("%d-%m-%y %H:%M:%S")
    get_date.short_description = "Date"