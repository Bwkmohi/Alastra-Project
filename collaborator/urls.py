from django.urls import path
from . import views
app_name = 'coll'
shop_id = '<int:shop_id>'

urlpatterns = [
    path(f'{shop_id}/collaborators_list/',views.collaborators_list,name='collaborators_list'),
    path(f'{shop_id}/collaborator/add/', views.collaborator_add, name='collaborator_add'),
    path(f'{shop_id}/collaborator/edit/<int:coll_id>/',views.collaborator_edit,name='collaborator_edit'),
    path(f'{shop_id}/collaborator/delete/<int:coll_id>/',views.collaborator_delete,name='collaborator_delete'),
    path(f'{shop_id}/collab_activity/<int:collab_id>/',views.collab_activity,name='collab_activity')
]