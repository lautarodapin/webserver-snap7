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
    list_display = ["id", "area", "created_at", "dato"]

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Fila)
class FilaAdmin(admin.ModelAdmin):
    list_display = ["id", "area", "name", "byte", "bit", "tipo_dato", "get_value"]

    def get_value(self, obj: Fila):
        return obj.read_value(obj.area.datos.first().dato)
    get_value.short_description = "Last value"