from django.urls import path
from . import views

urlpatterns = [
    path('',views.wallet_view,name='walet'),
    path('add_bank_cart_number',views.add_bank_cart_number,name='add_bank_cart_number')
]