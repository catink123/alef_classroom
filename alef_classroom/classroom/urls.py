from django.urls import path
from . import views

app_name = 'classroom'

urlpatterns = [
    path('', views.classroom_list, name='list'),
    path('create/', views.classroom_create, name='create'),
    path('<int:pk>/', views.classroom_detail, name='detail'),
    path('<int:pk>/edit/', views.classroom_edit, name='edit'),
    path('<int:pk>/delete/', views.classroom_delete, name='delete'),
    path('join/', views.classroom_join, name='join'),
    path('join/<int:pk>/', views.classroom_join, name='join_direct'),
    path('<int:classroom_pk>/announcement/create/', views.announcement_create, name='announcement_create'),
    path('announcement/<int:announcement_pk>/comment/', views.comment_create, name='comment_create'),
]
