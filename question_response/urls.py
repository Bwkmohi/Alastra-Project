from django.urls import path
from . import views

urlpatterns = [
    path('add_product_question/<int:id>/',views.add_product_question,name='add_product_question'),
]