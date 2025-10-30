# vpn_project/asgi.py

import os
import django
from django.core.asgi import get_asgi_application

# Устанавливаем переменную окружения Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vpn_project.settings')

# Инициализируем Django
django.setup()

# Импортируем ASGI-приложение Django ПОСЛЕ setup()
django_asgi_app = get_asgi_application()

# Импортируем наше Sio-приложение
from socketio_app import sio
import socketio

# Создаем ASGI-приложение, которое объединяет Django и Socket.IO
application = socketio.ASGIApp(sio, other_asgi_app=django_asgi_app)