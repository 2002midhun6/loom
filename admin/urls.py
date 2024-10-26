from django.urls import path,include
from . import views
app_name= 'admin_app'
urlpatterns = [
    path('admin_home',views.admin_home,name='admin_home'),
    path('user_details',views.user_details,name='user_details'),
    path('user_block/<id>/',views.user_block,name='user_block'),
    path('admin_logout',views.admin_logout,name='admin_logout')
]
