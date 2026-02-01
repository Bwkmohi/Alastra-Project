from django.urls import path
from . import views

urlpatterns = [
    path('apply/',views.coupon_apply,name='coupon_apply'),
    path('saved_coupon',views.saved_coupons,name='saved_coupons'),
    path('save_coupon/',views.save_coupon,name='save_coupon'),
    path('remove_coupon_from_saves/<int:id>/',views.remove_coupon_from_saves,name='remove_coupon')
]