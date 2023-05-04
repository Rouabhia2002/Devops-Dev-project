from django.urls import path
from . import views

urlpatterns = [
    path('run-script/', views.run_script, name='script'),
    path('amira/', views.amira, name='amira'),
    path('create_instance/', views.create_instance, name='create_instance'),
]