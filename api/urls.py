from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('run-script/', views.run_script, name='script'),
    path('login/', views.login, name='login'),
    #path('login_view/', views.login_view, name='login_view'),
    path('register/', views.register, name='register'),
    path('create_instance/', views.create_instance, name='create_instance'),
    path('stat/', views.get_instance_metrics, name='get_instance_metrics'),
    path('delete-ec2-instance/', views.delete_ec2_instance, name='delete_ec2_instance'),
    path('delete-ec2-instance-confirm/', views.delete_ec2_instance_confirm, name='delete_ec2_instance_confirm'),    path('update-instance/', views.update_instance_type, name='update_ec2_instance'),
    path('list-ec2-instances/', views.list_ec2_instances, name='list_ec2_instances'),
    path('update-ec2-instance/', views.update_instance_type, name='update_instance_type'),
    path('confirm-update-instance/', views.confirm_update_instance, name='confirm_update_type'),
    path('get_instance_statistics/', views.get_instance_statistics, name='get_instance_statistics'),

]
# Add the static URL configuration
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
