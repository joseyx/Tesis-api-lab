from django.urls import include, path
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

from tesis.chatbot import views

router = routers.DefaultRouter()

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
# urlpatterns = [
#     path("chatbot/", views.ChatbotView.as_view({'get': 'get', 'post': 'post'}), name="chatbot"),
#     path("", include(router.urls)),
#     path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
# ]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('tesis.users.urls')),
    path('api/', include('tesis.citas.urls')),
    path('api/', include('tesis.chatbot.urls')),
    path("", include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
