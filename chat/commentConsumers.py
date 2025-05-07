from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
from .models import Comment, Post, Notification
from django.contrib.auth import get_user_model

User = get_user_model()

class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.post_id = self.scope['url_route']['kwargs']['post_id']
        self.room_group_name = f'post_{self.post_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        comment_text = data['comment']
        username = data['username']

        # Sauvegarde et récupère l’auteur du post
        username, post_author_id = await self.save_comment(username, comment_text)
        comment_count = await self.get_comment_count()

        # Envoyer le commentaire à tous
        # group_send dans save_comment ou like
        await self.channel_layer.group_send(
            f'notifications_{post.author.id}',
            {
                'type': 'send_notification',
                'message': f"a commenté votre post.",
                'sender_id': user.id,
                'post_id': post.id,
            }
        )

        # Si l'auteur du post est différent de l'émetteur, envoyer la notif
        if int(post_author_id) != self.scope["user"].id:
            await self.channel_layer.group_send(
                f'notifications_{post_author_id}',
                {
                    'type': 'send_notification',
                    'message': f"{username} a commenté votre post."
                }
            )

    @database_sync_to_async
    def get_user_data(self, user_id):
        user = User.objects.get(id=user_id)
        return {
            "username": user.username,
            "avatar": user.profile_picture.url
        }

    async def send_notification(self, event):
        sender_data = await self.get_user_data(event["sender_id"])
        await self.send(text_data=json.dumps({
            "username": sender_data["username"],
            "sender_avatar": sender_data["avatar"],
            "message": event["message"],
            "post_id": event["post_id"]
        }))

    async def comment_message(self, event):
        await self.send(text_data=json.dumps({
            'comment': event['comment'],
            'username': event['username'],
            'comment_count': event['comment_count'],
            'post_id': event['post_id'],
            'type': 'new_comment',
        }))

    @database_sync_to_async
    def get_user(self, username):
        return User.objects.get(username=username)

    @database_sync_to_async
    def save_comment(self, username, comment_text):
        user = User.objects.get(username=username)
        post = Post.objects.get(id=self.post_id)
        comment = Comment.objects.create(author=user, post=post, content=comment_text)

        #Créer une notification (si ce n'est pas l'auteur qui commente lui-même)
        if post.author != user:
            Notification.objects.create(
                user=post.author,
                sender=user,
                post=post,
                message=f"{user.username} a commenté votre post."
            )
            return user.username, post.author.id  # on retourne pour l’envoyer ensuite






class LikeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.post_id = self.scope['url_route']['kwargs']['post_id']
        self.room_group_name = f'post_{self.post_id}'

        # Joindre le groupe de likes du post
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Quitter le groupe de likes du post
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Recevoir un message WebSocket du client (quand un like est ajouté ou retiré)
    async def receive(self, text_data):
        data = json.loads(text_data)
        post_id = data['post_id']
        action = data['action']  # like ou unlike
        user = data['username']

        # Effectuer l'action sur le like
        post = await self.get_post(post_id)
        if action == 'like':
            post.likes.add(user)
        elif action == 'unlike':
            post.likes.remove(user)

        # Diffuser le nouveau nombre de likes au groupe
        like_count = post.likes.count()

        # Diffuser l'événement à tous les clients connectés
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'like_update',
                'like_count': like_count,
                'post_id': post_id
            }
        )

    # Recevoir un message du groupe
    async def like_update(self, event):
        like_count = event['like_count']
        post_id = event['post_id']

        # Envoyer le nombre de likes au client WebSocket
        await self.send(text_data=json.dumps({
            'like_count': like_count,
            'post_id': post_id
        }))

    @database_sync_to_async
    def get_post(self, post_id):
        return Post.objects.get(id=post_id)
