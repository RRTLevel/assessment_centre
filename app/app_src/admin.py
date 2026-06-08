from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .forms import DomainUserChangeForm
from .models import DomainUser, Note


class DomainUserAdmin(UserAdmin):

    form = DomainUserChangeForm


admin.site.unregister(User)
admin.site.register(DomainUser, DomainUserAdmin)

admin.site.register(Note)
