import json
from channels.generic.websocket import AsyncWebsocketConsumer, async_to_sync
from channels.db import database_sync_to_async

from .serializers import (DatoSerializer, Dato)

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
        text_data_json = json.loads(text_data)
        print(text_data)
        type_ = text_data_json.get("type")
        if type_:
            return await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type':type_,
                }
            )
        message = text_data_json['message']

        # Send message to room group
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
        datos = await self.get_datos()
        await self.send(text_data=json.dumps(datos))


    @database_sync_to_async
    def get_datos(self):
        return DatoSerializer(instance=Dato.objects.all(), many=True).data