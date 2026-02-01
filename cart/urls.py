from django.urls import path
from . import views
app_name = 'cart'

urlpatterns = [
    path(
        '',
        views.cart,
         name='cart'
         ),
    path(
        'cart_add/',
        views.cart_add,
        name='cart_add'
        ),
    path(
        'add_to_cart',
        views.add_to_cart,
        name='add_to_cart'
    ),
    path(
        'remove/<int:id>/',
        views.cart_remove,
        name='cart_remove'
    ),
    path(
        'plus/',
        views.cart_edit_quantity1,
        name='cart_edit_quantity1'
        ),
    path(
        'mines/',
        views.cart_edit_quantity2,
        name='cart_edit_quantity2'
        ),
    path(
        'cart_details/<int:id>/',
        views.cart_qty
    )
]