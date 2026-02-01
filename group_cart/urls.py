from django.urls import path
from . import views

app_name = 'group_c'

urlpatterns = [
    path('group_cart_view/<int:group_id>/',views.group_cart_view,name='group_cart_view'),
    path('create_group_cart',views.create_group_cart,name='create_group_cart'),
    path('add_users_to_group/<int:group_id>/',views.add_users_to_group,name='add_users_to_group'),
    path('remove_user_from_group/<int:user_id>/<int:group_id>/',views.remove_user_from_group,name='remove_user_from_group'),
    path('remove_product_from_cart/<int:group_id>/<int:cart_id>/',views.remove_product_from_cart,name='remove_product_from_cart'),
    path('get_export_from_cart/<int:group_id>/',views.get_export_from_cart,name='get_export_from_cart'),
    path('group_member_cart/<int:group_id>/<int:user_id>/',views.group_member_cart,name='group_member_cart')
]