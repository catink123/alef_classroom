from django.urls import path
from . import views

app_name = 'assignment'

urlpatterns = [
    # Assignment views for teachers
    path('create/<str:classroom_slug>/', views.assignment_create, name='create'),
    path('<int:pk>/edit/', views.assignment_edit, name='edit'),
    path('<int:pk>/delete/', views.assignment_delete, name='delete'),
    
    # Assignment views for all users
    path('<int:pk>/', views.assignment_detail, name='detail'),
    path('list/<str:classroom_slug>/', views.assignment_list, name='list'),
    
    # Submission views for students
    path('<int:assignment_id>/submit/', views.submission_create, name='submit'),
    path('submission/<int:pk>/edit/', views.submission_edit, name='edit_submission'),
    
    # Grading views for teachers
    path('<int:assignment_id>/submissions/', views.submission_list, name='submissions'),
    path('submission/<int:pk>/', views.submission_detail, name='submission_detail'),
    path('submission/<int:pk>/grade/', views.submission_grade, name='grade'),
    
    # Comment views
    path('<int:assignment_id>/comment/', views.assignment_comment, name='assignment_comment'),
    path('submission/<int:submission_id>/comment/', views.submission_comment, name='submission_comment'),
]
