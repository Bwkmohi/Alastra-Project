from django.urls import path
from . import views

app_name = 'ord'
shop_id = '<int:shop_id>'

urlpatterns = [
    path(f'{shop_id}/orders_list/',views.orders_list,name='orders_list'),
    path(f'{shop_id}/filter_reservs',views.filter_reservs,name='filter_reservs'),
    path(f'{shop_id}/update_reserv_detail/<int:id>/',views.update_reserv_detail,name='update_reserv_detail'),
    path(f'{shop_id}/export_orders_for_seller/',views.export_orders_for_seller,name='export_orders_for_seller'),
    path(f'{shop_id}/archive/', views.archive_list, name='archive_list'),
    path(f'{shop_id}/archive/<int:year>/', views.order_archive_detail, name='order_archive_year'),
    path(f'{shop_id}/archive/<int:year>/<int:month>/', views.order_archive_detail, name='order_archive_month'),
    path(f'{shop_id}/list_filtered_orders/<str:type_filter>/',views.list_filtered_orders,name='list_filtered_orders'),
]