from django.urls import path
from . import views

app_name = 'cou'
shop_id = '<int:shop_id>'

urlpatterns = [
    path(f'{shop_id}/',views.coupon_list,name='coupon_list'),
    path(f'{shop_id}/coupon/add/',views.coupon_add,name='coupon_add'),
    path(f'{shop_id}/coupon/delete/<int:id>/',views.coupon_delete,name='coupon_delete'),
    path(f'{shop_id}/coupon/coupon_edit/<int:id>/',views.coupon_edit,name='coupon_edit'),  
]