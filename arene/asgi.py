import os, django
from django.core.asgi import get_asgi_application
django.setup()
from channels.routing import ProtocolTypeRouter, URLRouter  # Importer ProtocolTypeRouter ici
from channels.auth import AuthMiddlewareStack
from chat.routing import websocket_urlpatterns  # Importer les URL de routing de artistapp

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arene.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns  # Utiliser le routing de artistapp
        )
    ),
})
