from django.contrib import admin
from .models import FolloweUnFollow

class FolloweUnFollowAdmin(admin.ModelAdmin):
    list_display = ('shop','user',)
    list_filter = ['shop','user',]
admin.site.register(FolloweUnFollow,FolloweUnFollowAdmin)