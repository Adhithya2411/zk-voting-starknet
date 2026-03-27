from django.urls import path
from . import views

urlpatterns = [
    path('generate-proof/', views.generate_proof, name='generate_proof'),
]