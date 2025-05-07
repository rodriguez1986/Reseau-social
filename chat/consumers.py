from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from django.utils import timezone
import json

from chat.models import Message, CustomUser, Post, Comment

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.sender_username = self.scope['url_route']['kwargs']['sender']
        self.receiver_username = self.scope['url_route']['kwargs']['receiver']

        # Pour éviter les doublons : ordonner les usernames
        usernames = sorted([self.sender_username, self.receiver_username])
        self.room_group_name = f'chat_{usernames[0]}_{usernames[1]}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Récupérer et envoyer l'historique
        messages = await self.get_chat_history(self.sender_username, self.receiver_username)
        for msg in messages:
            await self.send(text_data=json.dumps({
                'message': msg['content'],
                'sender': msg['sender'],
                'receiver': msg['receiver'],
                'timestamp': msg['timestamp'],
                'seen': msg['seen'],

                #'sender_picture': message.sender.picture.url
            }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender_username = data['sender']
        receiver_username = data['receiver']

        # Récupérer les objets utilisateurs
        sender = await self.get_user(sender_username)
        receiver = await self.get_user(receiver_username)

        # Sauvegarder le message
        saved_message = await self.create_message(sender, receiver, message)

        # Broadcast du message
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': saved_message['content'],
                'sender': saved_message['sender'],
                'receiver': saved_message['receiver'],
                'timestamp': saved_message['timestamp'],
                'seen': saved_message['seen'],
                #'sender_picture': event['sender_picture'],
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def get_user(self, username):
        return CustomUser.objects.get(username=username)

    @database_sync_to_async
    def create_message(self, sender, receiver, content):
        message = Message.objects.create(
            sender=sender,
            receiver=receiver,
            content=content,
            timestamp=timezone.now()
        )
        return {
            'sender': sender.username,
            'receiver': receiver.username,
            'content': content,
            'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'seen': message.seen,
            'sender_picture': sender.picture.url if sender.picture else '/static/default.png'
        }

    @database_sync_to_async
    def get_chat_history(self, sender_username, receiver_username):
        messages = Message.objects.filter(
            sender__username__in=[sender_username, receiver_username],
            receiver__username__in=[sender_username, receiver_username]
        ).order_by('timestamp')

        return [{
            'sender': msg.sender.username,
            'receiver': msg.receiver.username,
            'content': msg.content,
            'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'seen': msg.seen,
            'sender_picture': msg.sender.profile_picture.url if msg.sender.profile_picture else '/static/default.png'
        } for msg in messages]


