from django.urls import path
from . import views

app_name = 'rep'

urlpatterns = [
   path('reports_list/',views.reports_list,name='reports_list'),
   path('report_add/<int:shop_id>/',views.report_add,name='report_add'),
   path('report_detail/<int:id>/',views.report_detail,name='report_detail')
]