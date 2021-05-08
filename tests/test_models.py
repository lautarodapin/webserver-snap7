from app.fields import MultiType
from typing import Tuple
import pytest
from app.models import *

@pytest.fixture
def basic_models() -> Tuple[Plc, Area, Fila, Dato]:
    plc = Plc.objects.create(ip="127.0.0.1", rack=0, slot=0, port=112, nombre="test plc")
    area = Area.objects.create(plc=plc, area=Area.DB, nombre="area 1", numero=1, offset=10)
    fila = Fila.objects.create(area=area, name="fila 1", byte=0, bit=0, tipo_dato=Fila.BOOL)
    dato = Dato.objects.create(area=area, dato=bytearray(0b00001111))
    return plc, area, fila, dato
@pytest.mark.django_db
def test_plc_model():
    plc = Plc.objects.create(
        ip="127.0.0.1",
        rack=0,
        slot=0,
        nombre="test"
    )
    assert plc


@pytest.mark.django_db
def test_dato_procesado_model_bool(basic_models: Tuple[Plc, Area, Fila, Dato]):
    plc, area, fila, dato = basic_models

    dato_procesado = DatoProcesado.objects.create(
        plc=plc,
        area=area,
        fila=fila,
        raw_dato=dato,
        name="test",
        date=now(),
        dato=MultiType("bool", "True")
    )
    assert dato_procesado.dato.value == True
    assert dato_procesado.dato.type == "bool"


@pytest.mark.django_db
def test_dato_procesado_model_int(basic_models: Tuple[Plc, Area, Fila, Dato]):
    plc, area, fila, dato = basic_models
    dato_procesado = DatoProcesado.objects.create(
        plc=plc,
        area=area,
        fila=fila,
        raw_dato=dato,
        name="test",
        date=now(),
        dato=MultiType("int", 10.5)
    )
    assert dato_procesado.dato.value == 10
    
    
@pytest.mark.django_db
def test_dato_procesado_model_float(basic_models: Tuple[Plc, Area, Fila, Dato]):
    plc, area, fila, dato = basic_models
    dato_procesado = DatoProcesado.objects.create(
        plc=plc,
        area=area,
        fila=fila,
        raw_dato=dato,
        name="test",
        date=now(),
        dato=MultiType("float", 10.5)
    )
    assert dato_procesado.dato.value == 10.5

@pytest.mark.django_db
def test_dato_procesado_model_datetime(basic_models: Tuple[Plc, Area, Fila, Dato]):
    plc, area, fila, dato = basic_models
    today = now()
    dato_procesado = DatoProcesado.objects.create(
        plc=plc,
        area=area,
        fila=fila,
        raw_dato=dato,
        name="test",
        date=now(),
        dato=MultiType("datetime", str(today))
    )
    assert dato_procesado.dato.value == today