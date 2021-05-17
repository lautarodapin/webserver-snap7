from django.db.models.query import QuerySet
from djangochannelsrestframework.decorators import action
from rest_framework.serializers import Serializer
from app.models import DatoProcesado
from collections import OrderedDict
import json
from typing import Dict, List
from channels.generic.websocket import AsyncWebsocketConsumer, async_to_sync
from channels.db import database_sync_to_async
from django.core.paginator import Paginator
import pandas as pd
from django.db.models import Prefetch, F

import snap7.util as s7util

from .serializers import (ChartDataSerializer, DatoProcesadoSerializer, DatoSerializer, Dato)

class DatosConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'datos_consumer'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        print(text_data)
        text_data_json: Dict = json.loads(text_data)
        if text_data_json.get("type", None):
            return await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type':text_data_json.get("type"),
                    'page_number':text_data_json.get("page_number", 1),
                    'page_size':text_data_json.get("page_size", 1),
                }
            )
        message = text_data_json['message']
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def ws_get_datos(self, event):
        page_number = event.get("page_number", 1)
        page_size = event.get("page_size", 1)
        datos = await self.get_datos(page_size=page_size, page_number=page_number)
        await self.send(text_data=json.dumps(datos))


    @database_sync_to_async
    def get_datos(self, page_size=1, page_number=1):
        queryset = Dato.objects.filter(area__numero=1)\
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
                    ).order_by("created_at")
        paginator = Paginator(queryset, page_size)

        page_obj = paginator.get_page(page_number)
        # data = DatoSerializer(instance=page_obj.object_list, many=True).data

        df = pd.DataFrame(page_obj.object_list)
        df["resultado"] = list(map(get_datos, df.values))
        
        return OrderedDict([
                    ('count', paginator.count),
                    ('has_next', page_obj.has_next()),
                    ('has_previous', page_obj.has_previous()),
                    ('has_next', page_obj.has_next()),
                    ('num_pages', paginator.num_pages),
                    ('results', df.to_json()),
                    ('page_number', page_number),
                ])
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


from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.decorators import action
from .mixins import StreamedPaginatedListMixin
from .paginator import WebsocketLimitOffsetPagination
class DatoProcesadoConsumer(StreamedPaginatedListMixin, GenericAsyncAPIConsumer):
    queryset = DatoProcesado.objects.all()
    pagination_class = WebsocketLimitOffsetPagination
    serializer_class = ChartDataSerializer


    def get_queryset(self, **kwargs) -> QuerySet:
        queryset = super().get_queryset(**kwargs)
        filters = kwargs.pop("filters", None)
        if filters:
            return queryset.filter(**filters)\
                .values_list("dato", "date")
        return queryset\
                .values_list("dato", "date")
        
        
    def get_serializer(self, action_kwargs: Dict = None, *args, **kwargs) -> Serializer:
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.get_serializer_class(**action_kwargs)

        kwargs["context"] = self.get_serializer_context(**action_kwargs)

        instance: List[DatoProcesado] = kwargs["instance"]

        datos = {
            "x":map(lambda dato: dato[1], instance),
            "y":map(lambda dato: dato[0].value, instance),
            "mode":"markers",
            "type":"scatter",
        }

        return serializer_class(instance=datos)