from django.urls import path
from . import views

urlpatterns = [
    path('payout_to_user_wallet/',views.payout_to_user_wallet,name='payout_to_user_wallet')
]