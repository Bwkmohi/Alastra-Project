from django.urls import path
from . import views

app_name = 's_ques'
shop_id = '<int:shop_id>'

urlpatterns = [
    path(f'{shop_id}/list_questions/',views.list_questions,name='list_questions'),
    path(f'{shop_id}/list_responses/',views.list_responses,name='list_responses'),
    path(f'{shop_id}/list_comments/',views.list_comments,name='list_comments'),
    path(f'{shop_id}/reponse_to_question/<int:question_id>/',views.reponse_to_question,name='reponse_to_question'),
    path(f'{shop_id}/edit_reseponse/<int:reseponse_id>/',views.edit_reseponse,name='edit_reseponse'),
    path(f'{shop_id}/remove_response/<int:response_id>/',views.remove_response,name='remove_response'),
    path(f'{shop_id}/remove_comment/<int:comment_id>/',views.remove_comment,name='remove_comment'),   
]