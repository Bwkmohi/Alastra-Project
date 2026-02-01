from django.urls import path
from . import views

urlpatterns = [   
    path('change_password/',views.change_password,name='change_password'),
    path('create_password/',views.create_password,name='create_password'),
    path('enter_password/<str:redirect_url>/', views.check_secure_and_enter_password, name='enter_password'),
    path('edit_password_Data/',views.edit_password_data,name='edit_password_data'),
    path('froget_password/',views.froget_password,name='froget_password'),
    path('face_register/',views.face_register,name='face_register'),
    path('face_enter/',views.face_enter,name='face_enter')
]