from django.urls import path
from . import views

shop_id = '<int:shop_id>'
app_name = 'pro'

urlpatterns = [
    path(f'{shop_id}/products_list/',views.products_list,name='products_list'),
    path(f'{shop_id}/product/add/',views.add_product,name='product_Add'),
    path(f'{shop_id}/edit_product/<int:product_id>/',views.edit_product,name='edit_product'),
    path(f'{shop_id}/filter_product/',views.filter_product,name='filter_product'),
    path(f'{shop_id}/product_analysis/<int:product_id>/',views.product_analysis,name='product_analysis'),
    path(f'{shop_id}/product/remove/<int:id>/',views.product_delete,name='product_delete'),
    path(f'{shop_id}/products_data/',views.products_data,name='products_data'),
]