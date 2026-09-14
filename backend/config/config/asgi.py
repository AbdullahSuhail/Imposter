"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

# import os
# # import channels

# from channels.routing import ProtocolTypeRouter, URLRouter
# from django.core.asgi import get_asgi_application
# from channels.sessions import SessionMiddlewareStack

# from rooms.routing import websocket_urlpatterns

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# django_asgi_app = get_asgi_application()

# application = ProtocolTypeRouter({
#     "http": django_asgi_app,
#      "websocket": SessionMiddlewareStack(
#         URLRouter(websocket_urlpatterns)
#     ),
    
# })


import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.sessions import SessionMiddlewareStack

from rooms.routing import websocket_urlpatterns as room_websocket_urlpatterns
from game.routing import websocket_urlpatterns as game_websocket_urlpatterns



django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,

    "websocket": SessionMiddlewareStack(
        URLRouter(
            room_websocket_urlpatterns +
            game_websocket_urlpatterns
        )
    ),
})