from typing import Tuple
from types import SimpleNamespace
import pytest
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from rest_framework.authtoken.models import Token
from django.test import Client
from app.consumers import DatoProcesadoConsumer
from rest_framework import status
from app.fields import MultiType
from django.utils.timezone import now
from app.models import Plc, Area, DatoProcesado, Dato, Fila
import random

CANTIDAD_DATOS = 100

class AuthWebsocketCommunicator(WebsocketCommunicator):
    def __init__(self, application, path, headers=None, subprotocols=None, user=None):
        super(AuthWebsocketCommunicator, self).__init__(application, path, headers, subprotocols)
        if user is not None:
            self.scope['user'] = user

    async def receive_json_from(self, timeout=1):
        return SimpleNamespace(**await super().receive_json_from(timeout=timeout))

@pytest.fixture
async def initial_data():
    plc = await database_sync_to_async(Plc.objects.create)(ip="127.0.0.1", rack=0,slot=0,port=1012)
    area = await database_sync_to_async(Area.objects.create)(plc=plc, nombre="area 1", numero=1, offset=10, area=Area.DB)
    fila = await database_sync_to_async(Fila.objects.create)(name="fila 1", area=area, byte=0, bit=0, tipo_dato=Fila.BOOL)
    dato = await database_sync_to_async(Dato.objects.create)(area=area, dato=bytearray(10))
    datos_procesados = list([
        DatoProcesado(
            plc=plc,area=area,fila=fila,raw_dato=dato,
            date=now(),
            dato=MultiType(type="bool", value=random.choice(["True", "False"]))
        )
        for i in range(CANTIDAD_DATOS)
    ])
    dato_procesado = await database_sync_to_async(DatoProcesado.objects.bulk_create)(datos_procesados)

@pytest.fixture
async def communicator() -> AuthWebsocketCommunicator:
    communicator = AuthWebsocketCommunicator(DatoProcesadoConsumer.as_asgi(), f"/testws/")
    connected, subprotocol = await communicator.connect()
    assert connected
    return communicator


@pytest.mark.django_db()
@pytest.mark.asyncio
async def test_todo_consumer(
    communicator: AuthWebsocketCommunicator, 
    initial_data):
    LAST_OFFSET = 0
    LIMIT = 6
    await communicator.send_json_to(dict(
        action="list",
        request_id=1,
        limit=LIMIT
    ))
    response = await communicator.receive_json_from()
    while response.data["offset"] + len(response.data["results"]) < response.data["count"]:
        print(response)
        assert response
        assert response.response_status == 200
        assert response.data["results"].__len__() == LIMIT
        assert response.data["count"] == CANTIDAD_DATOS
        assert response.data["limit"] == LIMIT
        assert response.data["offset"] == LAST_OFFSET
        LAST_OFFSET += LIMIT
        response = await communicator.receive_json_from()

    assert response.data["offset"] + len(response.data["results"]) == response.data["count"]


    assert await communicator.receive_nothing()
  

    await communicator.disconnect()