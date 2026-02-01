from django.urls import path
from . import share_list
from . import views

urlpatterns = [
    path('<int:receiver_id>/<int:chat_home_id>/', views.chat_home, name='chat'),
    path('unseen_messages/<int:ch_id>/', views.messages_list, name='unseen_messages'),
    path('new_chat/',views.new_chat,name='new_chat'),
    path('list_chathomes/',views.list_chathomes,name='list_chathomes'),
    path('delete_message/', views.delete_message, name='delete_message'),
    path('add_to_favorites/<int:id>/',views.add_to_favorites,name='add_to_favorites'),
    path('delete_chat_home/<int:id>/',views.delete_chat_home,name='delete_chat_home'),
    path('send_message/', views.send_message, name='send_message'),
    path('add_to_black_list/<int:id>/',views.add_to_black_list,name='add_to_black_list'),
    path('remove_from_black_list/<int:id>/',views.remove_from_black_list,name='remove_from_black_list'),
    path('remove_from_favorites/<int:id>/',views.remove_from_favorites,name='remove_from_favorites'),
    path('send_selected_products/', share_list.send_selected_products, name='send_selected_products'),
]    