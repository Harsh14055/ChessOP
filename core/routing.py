from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'^ws/game/(?P<room_code>\w+)/$', consumers.ChessGameConsumer.as_asgi()),
    re_path(r'^ws/chess/(?P<room_code>\w+)/$', consumers.ChessGameConsumer.as_asgi()),
]