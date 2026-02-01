from django.urls import path
from . import views

app_name = 'supp'

urlpatterns = [
    path('',views.chat,name='chat_view') ,
    path('response_page/<int:chat_id>/',views.response_page,name='response_page'), 
    path('list_questions/',views.list_questions,name='list_questions'), 
    path('send_message/',views.send_message,name='send_message'),
    path('ajax-unseen-messages/<int:chat_id>/',views.fetch_unseen_messages),
    path('dashbord/',views.dashbord_supporter,name='dashbord'),
]