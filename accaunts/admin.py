from django.contrib import admin
from .models import UserAuthentication,NationalIDAuthentication

admin.site.register(UserAuthentication)
admin.site.register(NationalIDAuthentication)