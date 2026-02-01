from django.urls import path
from .views import best_selling_view,special_products
from . import views
urlpatterns = [
    path('best_selling/', best_selling_view, name='best_slng'),
    path('popular/', views.popular_products_view, name='popular'),
    path('spessial_products/', views.special_products, name='special'),
    path('my_follower_products/',views.my_following_shop_products,name='follower_products'),

      path('spess/',special_products),
      path('last-reservs/',views.get_smart_suggestions_from_reserv_history,name='last_reservs'),
      path('exemple_my-watchlist_products/',views.exemple_my_watchlist_products,name='watchlist_'),
      path('last_viewed_products/',views.last_viewed_products,name='last_viewed_products'),
      path('special_products/',views.special_products,name='special_products'),
      path('exemple_cart/',views.exemple_cart_products,name='exemp_cart'),
      path('viewests/',views.viewedest,name='viewedest'),
      path('sell_price/',views.sell_price_products,name='sell_price'),
]