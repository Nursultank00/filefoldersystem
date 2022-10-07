from django.urls import path
from . import views

urlpatterns = [
    path('', views.ApiOverview, name = 'api_overview'),
    path('imports', views.ImportsView.as_view(), name = 'imports'),
    path('delete/<str:id>', views.DeleteView.as_view(), name = 'delete'),
]
