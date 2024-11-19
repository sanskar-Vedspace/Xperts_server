# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class PostConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Join the group for like updates
        await self.channel_layer.group_add(
            'like_updates',  # Group name for like updates
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the group
        await self.channel_layer.group_discard(
            'like_updates',  # Group name for like updates
            self.channel_name
        )

    async def like_update(self, event):
        # Send the like update to WebSocket
        await self.send(text_data=json.dumps({
            'post_id': event['post_id'],
            'is_liked': event['is_liked'],
            'likes_count': event['likes_count']
        }))
