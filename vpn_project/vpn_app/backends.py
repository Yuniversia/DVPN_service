# vpn_app/backends.py

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

CustomUser = get_user_model()

class UsernameOrEmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # В views.py 'username_or_email' передается как 'username' в authenticate
        # поэтому мы используем 'username' здесь.
        
        if username is None:
            # Если username не передан (например, в /admin), используем email из kwargs
            username = kwargs.get('email')

        if not username:
            return None
            
        try:
            # Пытаемся найти пользователя по username ИЛИ email
            user = CustomUser.objects.get(Q(username=username) | Q(email=username))
            
            # Проверяем пароль
            if user.check_password(password):
                return user
        except CustomUser.DoesNotExist:
            # Пользователь не найден
            return None
        except CustomUser.MultipleObjectsReturned:
            # На всякий случай, если данные некорректны (хотя unique=True должны это предотвратить)
            return CustomUser.objects.filter(Q(username=username) | Q(email=username)).first()

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None