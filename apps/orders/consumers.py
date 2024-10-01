import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class WSConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            await self.channel_layer.group_add("orders_notifications", self.channel_name)
            await self.accept()
            logger.info("WebSocket connected and added to group")
        except Exception as e:
            logger.error(f"Failed to connect: {e}")

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard("orders_notifications", self.channel_name)
            logger.info("WebSocket disconnected and removed from group")
        except Exception as e:
            logger.error(f"Failed to disconnect: {e}")

    async def send_notification(self, event):
        message = event['message']
        try:
            await self.send(text_data=json.dumps({'message': message}))
            logger.info(f"Notification sent: {message}")
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
