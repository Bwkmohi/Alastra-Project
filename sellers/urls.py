from django.urls import path
from . import views
 
app_name = 'sellers'
shop_id = '<int:shop_id>'

urlpatterns = [
    path(f'{shop_id}/',views.shop_dashbord,name='shop_dashbord'),
    path('seller_dashbord/',views.seller_dashbord,name='seller_dashbord'),
    path('create_shop/',views.create_shop,name='create_shop'),
    path(f'{shop_id}/shop_edit/', views.shop_edit, name='shop_edit'),
    path('become_seller/',views.become_seller,name='become_seller'),
    path(f'{shop_id}/shop_public_page/',views.shop_public_page,name='shop_public_page'),
    path('add_shop_rate/',views.add_shop_rate,name='add_shop_rate'),
    path('shop_search/',views.shop_search,name='shop_search')
]