from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('blog_detail/<int:id>/',views.blog_detail,name='blog_detail'),
    path('dashbord/',views.author_dashbord,name='author_dashbord'),
    path('filter/',views.filter,name='filter'),
    path('filter_blogs/<int:category_id>/',views.filter_blogs,name='filter_blogs'),
    path('add_blog/',views.blog_add,name='blog_add'),
    path('blog_edit/<int:blog_id>/',views.blog_edit,name='blog_edit'),
    path('delete/<int:blog_id>/', views.blog_delete, name='delete_blog'),
    path('become_author/',views.become_author,name='become_author'),
    path('author_edit/',views.author_edit,name='author_edit'),
    path('blog_search',views.blog_search,name='blog_search'),
    path('list_blogs/',views.list_blogs,name='list_blogs')
]
