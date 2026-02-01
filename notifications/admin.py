from django.contrib import admin
from .models import Notification,UserNotification,UserNotificationsSetting,Svg


admin.site.register(UserNotificationsSetting)
admin.site.register(Notification)
admin.site.register(UserNotification)
admin.site.register(Svg)