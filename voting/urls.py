from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'), 
    path('generate-proof/', views.generate_proof, name='generate_proof'), 
]