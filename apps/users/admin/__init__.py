from django.contrib import admin

from .tech_secret import TechSecret, TechSecretAdmin
from .user import User, UserAdmin

admin.site.register(User, UserAdmin)
admin.site.register(TechSecret, TechSecretAdmin)
