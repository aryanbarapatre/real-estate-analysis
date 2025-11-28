from django.urls import path
from . import views

urlpatterns = [
    path('analyze/', views.analyze_query, name='analyze_query'),
    path('health/', views.health_check, name='health_check'),
    path('upload/', views.upload_file, name='upload_file'),
    path('areas/', views.list_areas, name='list_areas'),
]

