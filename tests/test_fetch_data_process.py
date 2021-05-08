from datetime import timedelta
from app.fields import MultiType
from typing import Tuple
import pytest
from app.models import *
from rest_framework.test import APIClient
from rest_framework import status

ip = "127.0.0.1"
rack = 0
slot = 0
port = 1102

@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def basic_models() -> Tuple[Plc, Area, Fila, Dato]:
    plc = Plc.objects.create(ip=ip, rack=rack, slot=slot, port=port, nombre="test plc")
    area = Area.objects.create(plc=plc, area=Area.DB, nombre="area 1", numero=1, offset=10)
    fila = Fila.objects.create(area=area, name="fila 1", byte=0, bit=0, tipo_dato=Fila.INT)
    fila_2 = Fila.objects.create(area=area, name="fila 2", byte=2, bit=0, tipo_dato=Fila.INT)
    dato_1 = Dato.objects.create(area=area, dato=bytearray([100]))
    dato_2 = Dato.objects.create(area=area, dato=bytearray([150]))
    dato_3 = Dato.objects.create(area=area, dato=bytearray([200]))
    dato_4 = Dato.objects.create(area=area, dato=bytearray([0, 0, 200]))
    DatoProcesado.objects.create(area=area, plc=plc, fila=fila, raw_dato=dato_1, date=now(), dato=MultiType("int", 100))
    DatoProcesado.objects.create(area=area, plc=plc, fila=fila, raw_dato=dato_2, date=now() + timedelta(seconds=10), dato=MultiType("int", 150))
    DatoProcesado.objects.create(area=area, plc=plc, fila=fila, raw_dato=dato_3, date=now() + timedelta(seconds=20), dato=MultiType("int", 200))
    DatoProcesado.objects.create(area=area, plc=plc, fila=fila_2, raw_dato=dato_4, date=now(), dato=MultiType("int", 0))

@pytest.mark.django_db
def test_fetch_process_data_with_fila_filter(client: APIClient, basic_models):
    response = client.get("/api/datos-procesados/?fila__id=2")
    assert response.status_code == status.HTTP_200_OK

    assert response.data["results"].__len__() == 1

@pytest.mark.django_db
def test_fetch_process_data(client: APIClient, basic_models):
    response = client.get("/api/datos-procesados/?fila__id=1")
    assert response.status_code == status.HTTP_200_OK

    assert response.data["results"].__len__() == 3
    assert response.data["results"][0]["id"] == 1
    assert response.data["results"][1]["id"] == 2
    assert response.data["results"][2]["id"] == 3

    assert response.data["results"][0]["dato"] == 100
    assert response.data["results"][1]["dato"] == 150
    assert response.data["results"][2]["dato"] == 200

