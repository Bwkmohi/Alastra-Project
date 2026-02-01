from django.urls import path
from . import views
app_name = 'follow'

urlpatterns = [
        path(
            'follow-unfollow/',
            views.follow,
            name='follow'
        ),
        path(
            'list_followers/<int:shop_id>',
            views.list_followers,
            name='list_followers'
        ),
    ]