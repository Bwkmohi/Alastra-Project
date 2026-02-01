from django.urls import path
from . import views

app_name = 'res'

urlpatterns = [
    path('',views.reservation,name='res'),
    path('list_reservations/',views.list_reservations,name='list_reservations'),
    path('user_addreses/',views.user_addreses,name='user_addreses'),
    path('reservation_with_group_cart/<int:group_id>/',views.reservation_with_group_cart,name='reservation_with_group_cart'),
    path('pay_with_walet/<int:order_id>/',views.pay_with_walet,name='pay_with_walet'),
    path('order_detail/<int:id>/',views.order_detail,name='order_detail'),
    path('cancel-order/<int:reserv_id>/',views.cancel_order,name='cancel_order'),
    path('repeat_purchase/<int:order_id>/<str:pay_type>/',views.repeat_purchase,name='repeat_purchase'),
    path('pay_again/<int:order_id>/<str:pay_with>/',views.pay_again,name='pay_again'),
    path('order_export/<int:order_id>/',views.order_export,name='order_export')
]