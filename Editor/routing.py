from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from Editor.consumers import YourConsumer

application = ProtocolTypeRouter({
    "websocket": URLRouter(
        [
            path("ws/Editor/", YourConsumer.as_asgi()),
        ]
    ),
})
