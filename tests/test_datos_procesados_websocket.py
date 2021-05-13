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
class AuthWebsocketCommunicator(WebsocketCommunicator):
    def __init__(self, application, path, headers=None, subprotocols=None, user=None):
        super(AuthWebsocketCommunicator, self).__init__(application, path, headers, subprotocols)
        if user is not None:
            self.scope['user'] = user

    async def receive_json_from(self, timeout=1):
        return SimpleNamespace(**await super().receive_json_from(timeout=timeout))

@pytest.fixture()
def initial_data():
    plc = Plc.objects.create(ip="127.0.0.1", rack=0,slot=0,port=1012)
    area = Area.objects.create(plc=plc, nombre="area 1", numero=1, offset=10, area=Area.DB)
    fila = Fila.objects.create(name="fila 1", area=area, byte=0, bit=0, tipo_dato=Fila.BOOL)
    dato = Dato.objects.create(area=area, dato=bytearray(10))
    dato_procesado = DatoProcesado.objects.create(
        plc=plc,area=area,fila=fila,raw_dato=dato,
        date=now(),
        dato=MultiType(type="bool", value="True")
    )

@pytest.mark.django_db()
@pytest.mark.asyncio
async def test_todo_consumer(initial_data):
    communicator = AuthWebsocketCommunicator(DatoProcesadoConsumer.as_asgi(), f"/testws/")
    connected, subprotocol = await communicator.connect()
    assert connected

    await communicator.send_json_to(dict(
        action="list",
        request_id=1,
    ))

    response = await communicator.receive_json_from()
    print(response)
    assert response.response_status == 200


    await communicator.disconnect()