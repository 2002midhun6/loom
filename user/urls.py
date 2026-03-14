from django.urls import path
from . import views

app_name = 'user_app'

urlpatterns = [
    path('login/',          views.user_login,         name='user_login'),
    path('signup/',         views.sign_up,            name='sign_up'),
    path('otp/',            views.enter_otp,          name='enter_otp'),
    path('otp/resend/',     views.resend_otp,         name='resend_otp'),
    path('password/forgot/', views.forget_password,   name='forget_password'),
    path('password/otp/',   views.enter_otp_password, name='enter_otp_password'),
    path('password/check/', views.password_check,     name='password_check'),
    path('',                views.index,              name='index'),
    path('logout/',         views.user_logout,        name='user_logout'),
]

