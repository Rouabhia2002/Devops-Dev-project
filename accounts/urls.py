from django.urls  import path
from . import views
from django.contrib import admin

#app_name= 'accounts'

urlpatterns=[
    path('logout/', views.logout_view, name= 'logout'),
    path('login/', views.login_view, name= 'login'),
    #path('register/', views.register, name= 'register'),
    path('index/', views.index, name= 'index'),
    path('admin/', admin.site.urls),
]