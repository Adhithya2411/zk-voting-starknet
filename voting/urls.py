from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='landing'), name='logout'),
    
    path('voter/dashboard/', views.voter_dashboard, name='voter_dashboard'),
    path('voter/election/<int:election_id>/', views.vote_election, name='vote_election'),
    
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    path('generate-proof/', views.generate_proof, name='generate_proof'),
    path('bind-wallet/', views.bind_wallet, name='bind_wallet'),
]