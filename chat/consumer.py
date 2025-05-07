from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

from chat.models import Message  # Assurez-vous que le modèle Message est correctement importé

User = get_user_model()


async def broadcast_user_status(username, status):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        'users_status',
        {
            'type': 'user.status',
            'username': username,
            'status': status  # "online" ou "offline"
        }
    )


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.sender_username = self.scope['url_route']['kwargs']['sender_username']
        self.receiver_username = self.scope['url_route']['kwargs']['receiver_username']

        self.room_name = self.get_room_name(self.sender_username, self.receiver_username)
        self.room_group_name = f'chat_{self.room_name}'

        # Rejoindre le groupe de discussion
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.channel_layer.group_add('users_status', self.channel_name)
        await self.accept()
        await broadcast_user_status(self.scope["user"].username, "online")


        # Envoyer l'historique des messages
        messages = await self.get_chat_history(self.sender_username, self.receiver_username)
        for message in messages:
            await self.send(text_data=json.dumps({
                'type': 'chat_message',
                'message': message['content'],
                'sender': message['sender'],
                'seen': message['seen'],
                'timestamp': message['timestamp'].isoformat()
            }))

        # Envoyer le statut en ligne
        await self.send(text_data=json.dumps({
            'type': 'user_status',
            'status': 'online'
        }))

    async def disconnect(self, close_code):
        # Quitter le groupe de discussion
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        await self.channel_layer.group_discard('users_status', self.channel_name)
        await broadcast_user_status(self.scope["user"].username, "offline")

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message')
        sender_username = data.get('sender')
        receiver_username = data.get('receiver')

        if message and sender_username and receiver_username:
            # Sauvegarder le message
            await self.save_message(sender_username, receiver_username, message)

            # Envoyer le message au groupe
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': sender_username,
                    'seen': False,
                    'timestamp': timezone.now().isoformat()
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'sender': event['sender'],
            'seen': event['seen'],
            'timestamp': event['timestamp']
        }))

    @staticmethod
    def get_room_name(user1, user2):
        return '_'.join(sorted([user1, user2]))

    @database_sync_to_async
    def get_chat_history(self, user1_username, user2_username):
        user1 = User.objects.get(username=user1_username)
        user2 = User.objects.get(username=user2_username)
        messages = Message.objects.filter(
            sender__in=[user1, user2],
            receiver__in=[user1, user2]
        ).order_by('timestamp')
        return [
            {
                'content': msg.content,
                'sender': msg.sender.username,
                'seen': msg.seen,
                'timestamp': msg.timestamp
            }
            for msg in messages
        ]

    @database_sync_to_async
    def save_message(self, sender_username, receiver_username, content):
        sender = User.objects.get(username=sender_username)
        receiver = User.objects.get(username=receiver_username)
        Message.objects.create(sender=sender, receiver=receiver, content=content)




    async def user_status(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user-status-update',
            'username': event['username'],
            'status': event['status']
        }))

class StatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'users_status'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def user_status(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user-status-update',
            'username': event['username'],
            'status': event['status']
        }))


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.user_id_url = self.scope['url_route']['kwargs']['user_id']  # récupère ID depuis l'URL

        if self.user.is_authenticated and str(self.user.id) == self.user_id_url:
            self.group_name = f'notifications_{self.user.id}'
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        pass  # On ne reçoit rien du client, on push seulement


