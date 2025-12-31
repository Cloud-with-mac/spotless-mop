from django.urls import path
from . import views

urlpatterns = [
    # Public site
    path('', views.index, name='index'),
    
    # Custom Admin URLs
    path('admin-panel/', views.admin_login, name='admin_login'),
    path('admin-panel/logout/', views.admin_logout, name='admin_logout'),
    path('admin-panel/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Quote Management
    path('admin-panel/quotes/', views.admin_quotes_list, name='admin_quotes_list'),
    path('admin-panel/quotes/<int:pk>/', views.admin_quote_detail, name='admin_quote_detail'),
    path('admin-panel/quotes/<int:pk>/delete/', views.admin_quote_delete, name='admin_quote_delete'),
    
    # Service Management
    path('admin-panel/services/', views.admin_services_list, name='admin_services_list'),
    path('admin-panel/services/create/', views.admin_service_create, name='admin_service_create'),
    path('admin-panel/services/<int:pk>/edit/', views.admin_service_edit, name='admin_service_edit'),
    path('admin-panel/services/<int:pk>/delete/', views.admin_service_delete, name='admin_service_delete'),
    
    # Testimonial Management
    path('admin-panel/testimonials/', views.admin_testimonials_list, name='admin_testimonials_list'),
    path('admin-panel/testimonials/create/', views.admin_testimonial_create, name='admin_testimonial_create'),
    path('admin-panel/testimonials/<int:pk>/edit/', views.admin_testimonial_edit, name='admin_testimonial_edit'),
    path('admin-panel/testimonials/<int:pk>/delete/', views.admin_testimonial_delete, name='admin_testimonial_delete'),
    
    # Settings
    path('admin-panel/settings/', views.admin_settings, name='admin_settings'),
]
