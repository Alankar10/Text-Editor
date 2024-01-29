import json
from channels.generic.websocket import AsyncWebsocketConsumer

class YourConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Add the consumer to the WebSocket group
        await self.channel_layer.group_add(
            'text_files',  # Customize this group name as needed
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Remove the consumer from the WebSocket group
        await self.channel_layer.group_discard(
            'text_files',  # Customize this group name as needed
            self.channel_name
        )

    async def receive(self, text_data):
        # Handle received messages, modify as needed
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Echo the received message back to the sender, modify as needed
        await self.send(text_data=json.dumps({"message": message}))

    async def file_changed(self, event):
        # Notify clients in the group about file changes
        await self.send(text_data=json.dumps({
            'message': 'File changed!',
        }))
