from django.urls import path
from . import views

app_name = 'pvideo'
shop_id = '<int:shop_id>'

urlpatterns = [
    path(f'{shop_id}/add_video/',views.add_video,name='add_video'),
    path(f'{shop_id}/remove_video/<int:video_id>/',views.remove_video,name='remove_video'),
    path(f'{shop_id}/edit_product_video/<int:video_id>/',views.edit_product_video,name='edit_product_video'),
    path(f'{shop_id}/list_videos/',views.list_videos,name='list_videos'),
]