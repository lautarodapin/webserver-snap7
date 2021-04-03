from typing import List
from .models import *
from .fields import MultiType
import pandas as pd


def procesar_datos():
    queryset = Dato.objects\
        .filter(procesado=False)\
        .select_related("area", "area__plc")\
        .prefetch_related("area__filas")\
        .values(
            "created_at", 
            "area__area", 
            "dato", 
            "area__filas__name", 
            "area__filas__byte", 
            "area__filas__bit", 
            "area__filas__tipo_dato",
            "area__filas__id",
            "area__id",
            "area__offset",
            "area__id",
            "area__filas__id",
        )
    df = pd.DataFrame(queryset)
    df["resultado"] = list(map(get_datos, df.values))
    datos_procesados : List[DatoProcesado] = []
    for i, row in df.iterrows():
        tipo_dato = row.area__filas__tipo_dato
        tipo_dato = "bool" if tipo_dato == "get_bool" else "int" if "get_int" else "real"  # todo
        dato_procesado = DatoProcesado(
            area_id=row.area__id,
            fila_id=row.area__filas__id,
            name=row.area__filas__name,
            date=row.created_at,
            dato=MultiType(tipo_dato, str(row.resultado)),
        )                
        datos_procesados.append(dato_procesado)
    DatoProcesado.objects.bulk_create(datos_procesados)
    queryset.update(procesado=True)

def _len_check(_bytearray, index):
    return len(bytearray(_bytearray)) > index

def get_datos(array):
        function = getattr(s7util, array[6])
        dato = bytearray(array[2])
#         if _len_check(dato, array[9]):
        if array[6] == "get_bool":
            return function(dato, int(array[4]), int(array[5]))
        return function(dato, int(array[4]))
        return np.nan
def map_datos(array):
    return list(map(get_datos, array))