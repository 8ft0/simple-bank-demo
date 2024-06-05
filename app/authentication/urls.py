from django.urls import path
from django.contrib.auth import views as auth_views
from .views import register, login_view, home, create_account, delete_account, account_list, deposit, withdraw, transfer, transaction_history

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logged_out.html'), name='logout'),
    path('home/', home, name='home'),
    path('create_account/', create_account, name='create_account'),
    path('delete_account/<int:account_id>/', delete_account, name='delete_account'),
    path('accounts/', account_list, name='account_list'),
    path('deposit/<int:account_id>/', deposit, name='deposit'),
    path('withdraw/<int:account_id>/', withdraw, name='withdraw'),
    path('transfer/<int:account_id>/', transfer, name='transfer'),
    path('transactions/<int:account_id>/', transaction_history, name='transaction_history'),
]
