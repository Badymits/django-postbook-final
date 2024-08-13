"""
ASGI config for postbook project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack # supports django authentication where user details are stored in a session
import home.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postbook.settings')

application = ProtocolTypeRouter({
    'http':get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(home.routing.websocket_urlpatterns)
    )
})
