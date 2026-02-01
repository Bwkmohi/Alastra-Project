from django.contrib import admin
from .models import Message,ChatHome,BlackList

admin.site.register(Message)
admin.site.register(ChatHome)
admin.site.register(BlackList)