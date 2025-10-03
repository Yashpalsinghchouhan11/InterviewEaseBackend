from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import signupModel

class MyAdmin(admin.ModelAdmin):
    search_fields = ('email', 'username')

admin.site.register(signupModel, MyAdmin)
