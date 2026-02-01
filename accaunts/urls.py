from django.urls import path
from . import views
app_name = 'acc'

urlpatterns = [
    path('signup/',views.signup,name='sign'),
    path('send_otp_to_email/',views.send_otp_to_email,name='send_otp_to_email'),
    path('verify_email/',views.verify_email,name='verify_email'),
    path('login/',views.login_view,name='login'),
    path('authentication/', views.authentication, name='authentication'),
    path('logout/',views.logout_view,name='logout'),
    path('profile/',views.profile,name='pro'),
    path('user_edit/', views.user_edit, name='user_edit'),
    path('send_reset_password_link/',views.send_reset_password_link,name='send_reset_password_link'),
    path('password_reset_confirm/<str:uidb64>/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('authentication/e/',views.edit_authentication_user,name='edit_authentication_user'),
    # path('authentication_with_nation_cart_image/',views.authentication_with_nation_cart_image,name='authentication_with_nation_cart_image'),
]

                        