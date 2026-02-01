from django.urls import path
from . import views

app_name = 'notf'
urlpatterns = [
    path('',views.notifications_list,name='notifications'),
    path('ajax/notifications_setting/email/',views.close_or_open_email_notifications),
    path('ajax/notifications_setting/site/',views.close_or_open_site_notifications),
    path('ajax/notifications_statuses/',views.show_defult_notification_status),
]