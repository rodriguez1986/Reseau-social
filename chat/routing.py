from django.urls import re_path
from chat.consumer import ChatConsumer,StatusConsumer,NotificationConsumer
from chat.commentConsumers import CommentConsumer, LikeConsumer


websocket_urlpatterns = [
    re_path(r'^ws/chat/(?P<sender_username>\w+)/(?P<receiver_username>\w+)/$', ChatConsumer.as_asgi()),
    re_path(r'ws/comments/(?P<post_id>\d+)/$', CommentConsumer.as_asgi()),
    re_path(r'^ws/status/$', StatusConsumer.as_asgi()),
    re_path(r'ws/notifications/(?P<user_id>\d+)/$', NotificationConsumer.as_asgi()),
    re_path('ws/likes/<int:post_id>/', LikeConsumer.as_asgi()),
]


