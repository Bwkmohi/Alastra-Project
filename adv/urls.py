from django.urls import path
from . import views
app_name = 'adv'

urlpatterns = [
    path('',views.indexPage,name='indexpage'),
    path('project_detail/<int:id>/<slug:slug>/',views.project_detail,name='project_detail'),
]                 