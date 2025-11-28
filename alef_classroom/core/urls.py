"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from .views import (
    HomeView, dashboard_view, 
    dashboard_classroom_stats, dashboard_enrolled_stats,
    dashboard_assignment_stats, dashboard_pending_stats,
    dashboard_recent_classes, dashboard_recent_activity
)
from .admin_views import (
    admin_dashboard, admin_users, admin_classrooms, admin_submissions
)
from .health import health_check

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('dashboard/', dashboard_view, name='dashboard'),
    
    # HTMX Dashboard endpoints
    path('dashboard/stats/classrooms/', dashboard_classroom_stats, name='dashboard_classroom_stats'),
    path('dashboard/stats/enrolled/', dashboard_enrolled_stats, name='dashboard_enrolled_stats'),
    path('dashboard/stats/assignments/', dashboard_assignment_stats, name='dashboard_assignment_stats'),
    path('dashboard/stats/pending/', dashboard_pending_stats, name='dashboard_pending_stats'),
    path('dashboard/recent-classes/', dashboard_recent_classes, name='dashboard_recent_classes'),
    path('dashboard/recent-activity/', dashboard_recent_activity, name='dashboard_recent_activity'),
    
    # Admin supervision URLs
    path('admin-panel/', admin_dashboard, name='admin_dashboard'),
    path('admin-panel/users/', admin_users, name='admin_users'),
    path('admin-panel/classrooms/', admin_classrooms, name='admin_classrooms'),
    path('admin-panel/submissions/', admin_submissions, name='admin_submissions'),
    
    # Health check
    path('health/', health_check, name='health_check'),
    
    # App URLs
    path('accounts/', include('accounts.urls')),
    path('classroom/', include('classroom.urls')),
    path('assignment/', include('assignment.urls')),
    path('api-auth/', include('rest_framework.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
