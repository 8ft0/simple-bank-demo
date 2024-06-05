from django.urls import path
from .views import chat_view, chat_page_view

urlpatterns = [
    path('chat/', chat_view, name='chat'),
    path('chat-page/', chat_page_view, name='chat_page'),
]
