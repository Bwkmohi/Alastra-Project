from django.urls import path
from . import views
 
app_name = 'com'
urlpatterns = [
    path('add_to_compare/<int:product_id>/',views.add_product_to_compare,name='add_to_compare'),
    path('compare/',views.compare_view,name='compare_view'),
    path('remove-compare/<int:id>/',views.remove_from_compare,name='remove_from_compare'),
    path('add_to_compare_by_list/',views.add_to_compare_by_list,name='add_to_compare_by_list')
]