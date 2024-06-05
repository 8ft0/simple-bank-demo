from django.urls import path
from django.contrib.auth import views as auth_views
from .views import register, login_view, home

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logged_out.html'), name='logout'),
    path('home/', home, name='home'),
]
