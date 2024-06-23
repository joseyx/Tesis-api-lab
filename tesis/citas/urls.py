from django.urls import path
from .views import CitasCreateView, CitasListView, CitasDetailView, CitasAllView


urlpatterns = [
    path('citas', CitasCreateView.as_view(), name='citas-create'),
    path('citas/list', CitasListView.as_view(), name='citas-list'),
    path('citas/list/all', CitasAllView.as_view(), name='citas-list-all'),
    path('citas/<int:id>', CitasDetailView.as_view(), name='citas-detail')
]