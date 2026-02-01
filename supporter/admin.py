from django.contrib import admin
from .models import ChatMessages,ChatView,SupporterActivity,Supporter



admin.site.register(SupporterActivity)
admin.site.register(Supporter)
admin.site.register(ChatMessages)
admin.site.register(ChatView)