from typing import List
from .models import *
from .fields import MultiType
from .utils import MATCH_TYPES
import pandas as pd

def get_queryset_to_fetch(ids: List[int]):
    queryset = Area.objects\
        .filter(pk__in=ids)\
        .select_related("plc__ip", "plc__rack", "plc__slot", "plc__port")\
        .values(
            "id",
            "plc__ip",
            "plc__rack",
            "plc__slot",
            "plc__port",
            "area",
            "numero",
            "offset",
        )
    return queryset


def fetch_data_from_plc(ids: List[int], **kwargs):
    queryset = get_queryset_to_fetch(ids)
    for area in queryset.iterator(chunk_size=100):
        client: Client = Client()
        client.connect(
            area.get("plc__ip"),
            area.get("plc__rack"),
            area.get("plc__slot"),
            area.get("plc__port")
        )
        assert client.get_connected()
        datos = client.read_area(
            area=area.get("area"),
            dbnumber=area.get("numero"),
            start=0,
            size=area.get("offset"),
        )
        
        dato: Dato = Dato.objects.create(
            area_id=area.get("id"),
            dato=datos,
        )

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
            "area__plc",
        )
    df = pd.DataFrame(queryset)
    df["resultado"] = list(map(get_datos, df.values))
    datos_procesados : List[DatoProcesado] = []
    for i, row in df.iterrows():
        tipo_dato = row.area__filas__tipo_dato
        tipo_dato = MATCH_TYPES[tipo_dato]
        dato_procesado = DatoProcesado(
            area_id=row.area__id,
            fila_id=row.area__filas__id,
            plc_id=row.area__plc,
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
        fuc = getattr(s7util, array[6])
        dato = bytearray(array[2])
#         if _len_check(dato, array[9]):
        if array[6] == "get_bool":
            return fuc(dato, int(array[4]), int(array[5]))
        return fuc(dato, int(array[4]))
        return np.nan

def map_datos(array):
    return list(map(get_datos, array))