from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.user_login,name='user_login'),
    path('sign_up',views.sign_up,name='sign_up'),
    path('enter_otp',views.enter_otp,name='enter_otp'),
    path('resend_otp',views.resend_otp,name='resend_otp'),
    path('forget_password',views.forget_password,name='forget_password'),
    path('enter_otp_password',views.enter_otp_password,name='enter_otp_password'),
    path('password_check',views.password_check,name='password_check'),
    path('index',views.index,name='index')
   


]

