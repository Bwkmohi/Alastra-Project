from django.urls import path
from .views import zarinpal_request, zarinpal_verify,start_deposit_to_wallet,verify_deposit_to_wallet,withdraw_view


urlpatterns = [
    path('zarinpal/request/<int:order_id>/', zarinpal_request, name='zarinpal_request'),
    path('zarinpal/verify/', zarinpal_verify, name='zarinpal_verify'),
    path('start_deposit_to_wallet',start_deposit_to_wallet,name='start_deposit_to_wallet'),
    path('verify_deposit_to_wallet/',verify_deposit_to_wallet,name='verify_deposit_to_wallet'),

    path('withdraw_view/',withdraw_view,name='withdraw_view'),


    
]