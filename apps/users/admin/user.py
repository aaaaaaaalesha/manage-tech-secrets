from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import SetUnusablePasswordMixin

from apps.users.forms import UserCreationForm, UserChangeForm
from apps.users.models import User


class AdminUserCreationForm(SetUnusablePasswordMixin, UserCreationForm):
    usable_password = SetUnusablePasswordMixin.create_usable_password_field()


class UserAdmin(BaseUserAdmin):
    model = User
    add_form = AdminUserCreationForm
    form = UserChangeForm
    list_display = ("username", "email", "type",)
    list_filter = BaseUserAdmin.list_filter + ("type",)

    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {"fields": ("type",)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {"fields": ("type",)}),
    )
