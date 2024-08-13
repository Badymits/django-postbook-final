from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.loginView, name="login"),
    path('register/', views.registerView, name='register'),
    path('logout/', views.logoutView, name='logout'),
    path('user/<int:id>/<str:tab>/', views.userView, name='user'),
    path('settings/<str:tab>/', views.settingsView, name='settings'),
    
    path('edit-profile/<int:id>/', views.editProfile, name='edit-profile'),
]
