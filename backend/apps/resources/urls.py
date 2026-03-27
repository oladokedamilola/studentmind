# apps/resources/urls.py
from django.urls import path
from . import views

app_name = 'resources'

urlpatterns = [
    path('api/', views.get_resources_api, name='api_resources'),
    path('api/recommended/', views.get_recommended_resource, name='recommended'),
    path('api/search/', views.search_resources, name='search_resources'),
    path('api/featured/', views.get_featured_resources, name='featured_resources'),
    path('api/category/<str:category_name>/', views.get_resources_by_category, name='resources_by_category'),
    path('api/<int:resource_id>/save/', views.save_resource, name='save_resource'),
    path('api/<int:resource_id>/rate/', views.rate_resource, name='rate_resource'),
]