from django.urls import path
from .views import ChatbotView, InstructionListCreateAPIView, InstructionDetailAPIView,UserChatMessageCreateAPIView


urlpatterns = [
    path('chatbot/', ChatbotView.as_view(), name='chatbot'),
    path('instructions/', InstructionListCreateAPIView.as_view(), name='instruction-list-create'),
    path('instructions/<int:pk>/', InstructionDetailAPIView.as_view(), name='instruction-detail'),
    path('chat-messages/', UserChatMessageCreateAPIView.as_view(), name='chat-message-create'),
]