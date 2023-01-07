"""Details for admin panel for user."""

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


class UserAdmin(BaseUserAdmin):
    """Handle User admin."""

    list_display = ('email', 'first_name', 'last_name', 'is_superuser', 'is_staff', )
    list_filter = ('is_superuser', )
    fieldsets = (
        (None, {'fields': ('email', 'password', )}, ),
        ('Personal info', {'fields': ('first_name', 'last_name', )}),
        ('Permissions', {'fields': ('is_superuser', 'is_staff', )}, ),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide', ),
            'fields': (
                'email',
                'first_name',
                'last_name',
                'password',
                'confirm_password',
            ),
        }),
    )
    search_fields = ('email', )
    ordering = ('email', )
    filter_horizontal = ()


admin.site.register(get_user_model(), UserAdmin)
admin.site.unregister(Group)
