from django.urls import path
from . import views

shop_id = '<int:shop_id>'
app_name = 'story'

urlpatterns = [
    path(f'{shop_id}/add_story/',views.add_story,name='add_story'),
    path(f'{shop_id}/remove_story/<int:story_id>/',views.remove_story,name='remove_story'),
    path(f'{shop_id}/list_story/',views.list_story,name='list_story')
]