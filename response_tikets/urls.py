from django.urls import path
from . import views

urlpatterns = [
    path('filter_tikets/<int:category_id>/',views.filter_tikets,name='filter_tikets'),
    path('list_tikets/',views.list_tikets,name='list_tikets'),
    path('response_to_tiket/' ,views.response_to_tiket,name='response_to_tiket'),
]