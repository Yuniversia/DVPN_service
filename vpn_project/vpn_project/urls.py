# vpn_project/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('vpn_app.urls')), # Подключаем URL-ы нашего приложения
]