from django.urls import path
from . import views

app_name = 'gallery'
shop_id = '<int:shop_id>'

urlpatterns = [ 
    path(f'{shop_id}/add_gallery/',views.add_gallery,name='add_gallery'),
    path(f'{shop_id}/delete_gallery/<int:gallery_id>/',views.delete_gallery,name='delete_gallery'),
    path(f'{shop_id}/',views.list_product_gallery,name='list_product_gallery'),
    path(f'{shop_id}/edit_gallery/<int:gallery_id>/',views.edit_gallery,name = 'edit_gallery'),
    path('product_gallery/<int:product_id>/',views.product_gallery,name='product_gallery'),
]