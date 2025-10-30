# vpn_app/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Group, Link, Peer_link

# Настройка для CustomUser
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'current_group', 'group_ip', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active', 'current_group')
    
    # Поля, отображаемые при редактировании
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Timestamps', {'fields': ('last_login', 'date_joined')}),
        ('DVPN Info', {'fields': ('current_group', 'group_ip', 'peer_id')}),
    )
    # Поля, отображаемые при создании
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password'),
        }),
    )
    ordering = ('username',)

# Настройка для Group
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'ip_address', 'creator')
    search_fields = ('name', 'creator__username')
    filter_horizontal = ('group_admins',) # Удобный виджет для ManyToMany

# Настройка для Link
class LinkAdmin(admin.ModelAdmin):
    list_display = ('link_code', 'group', 'author', 'max_uses', 'current_uses', 'expiration_time')
    list_filter = ('group', 'is_admin_link')
    search_fields = ('link_code', 'author__username')

# Настройка для Peer_link
class PeerLinkAdmin(admin.ModelAdmin):
    list_display = ('link', 'group', 'creator')
    search_fields = ('link', 'group__name', 'creator__username')

# Регистрация моделей
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Link, LinkAdmin)
admin.site.register(Peer_link, PeerLinkAdmin)