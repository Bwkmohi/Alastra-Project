from django.urls import path
from . import views

app_name = 'watchlist'

urlpatterns = [    
    path('',views.watch_list,name='watch_list'),
    path('watchlist/add/',views.watchlist_add,name='watchlist_add'),
    path('watchlist/remove/<int:id>/',views.watchlist_remove,name='watchlist_remove'),
    path('add_to_watchlist_by_list/',views.add_to_watchlist_by_list,name='add_to_watchlist_by_list'),
    path('remove_from_watchlist_by_list/',views.remove_from_watchlist_by_list,name='remove_from_watchlist_by_list'),
    path('add_or_edit_alert/',views.add_or_edit_alert,name='add_or_edit_alert'),
    path('add_cart_from_wactchlist/',views.add_cart_from_wactchlist,name='add_cart_from_wactchlist'),
    path('clear_watchlist/',views.clear_watchlist,name='clear_watchlist')
]