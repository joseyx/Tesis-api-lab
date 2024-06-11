from django.urls import include, path
from rest_framework import routers

from tesis.chatbot import views

router = routers.DefaultRouter()

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("chatbot/", views.ChatbotView.as_view({'get': 'get', 'post': 'post'}), name="chatbot"),
    path("", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
