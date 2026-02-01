from django.urls import path
from . import views

app_name = 'mess'

urlpatterns = [
    path('send_tiket/',views.send_tiket,name='send_tiket'),
    path('remove_tiket/<int:id>/',views.remove_tiket,name='remove_tiket'),
    path('edit_tiket/<int:id>/',views.edit_tiket,name='edit_tiket'),
    path('list_my_tikets/',views.list_my_tikets,name='list_my_tikets'),
]