from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from accounts.models import User, TeacherProfile, StudentProfile
from classroom.models import Classroom, ClassroomMember
from assignment.models import Assignment, AssignmentSubmission

def is_admin(user):
    """Check if user is an admin."""
    return user.is_authenticated and user.role == User.Role.ADMIN

@login_required
def admin_dashboard(request):
    """
    Admin dashboard for supervising all classrooms, users, and submissions.
    """
    if not is_admin(request.user):
        messages.error(request, "You don't have permission to access this page.")
        return HttpResponseForbidden("Access Denied")
    
    # Get statistics
    total_users = User.objects.count()
    total_teachers = User.objects.filter(role=User.Role.TEACHER).count()
    total_students = User.objects.filter(role=User.Role.STUDENT).count()
    total_admins = User.objects.filter(role=User.Role.ADMIN).count()
    
    total_classrooms = Classroom.objects.count()
    active_classrooms = Classroom.objects.filter(is_active=True).count()
    archived_classrooms = Classroom.objects.filter(is_archived=True).count()
    
    total_assignments = Assignment.objects.count()
    total_submissions = AssignmentSubmission.objects.count()
    graded_submissions = AssignmentSubmission.objects.filter(is_graded=True).count()
    pending_submissions = AssignmentSubmission.objects.filter(is_graded=False).count()
    
    # Get recent activity
    recent_classrooms = Classroom.objects.all().order_by('-created_at')[:5]
    recent_assignments = Assignment.objects.all().order_by('-created_at')[:5]
    recent_submissions = AssignmentSubmission.objects.all().order_by('-submitted_at')[:5]
    
    context = {
        'total_users': total_users,
        'total_teachers': total_teachers,
        'total_students': total_students,
        'total_admins': total_admins,
        'total_classrooms': total_classrooms,
        'active_classrooms': active_classrooms,
        'archived_classrooms': archived_classrooms,
        'total_assignments': total_assignments,
        'total_submissions': total_submissions,
        'graded_submissions': graded_submissions,
        'pending_submissions': pending_submissions,
        'recent_classrooms': recent_classrooms,
        'recent_assignments': recent_assignments,
        'recent_submissions': recent_submissions,
    }
    
    return render(request, 'admin/dashboard.html', context)

@login_required
def admin_users(request):
    """
    Admin page to view and manage all users.
    """
    if not is_admin(request.user):
        messages.error(request, "You don't have permission to access this page.")
        return HttpResponseForbidden("Access Denied")
    
    users = User.objects.all().order_by('-date_joined')
    
    # Filter by role if specified
    role_filter = request.GET.get('role')
    if role_filter:
        users = users.filter(role=role_filter)
    
    context = {
        'users': users,
        'role_filter': role_filter,
        'roles': User.Role.choices,
    }
    
    return render(request, 'admin/users.html', context)

@login_required
def admin_classrooms(request):
    """
    Admin page to view and manage all classrooms.
    """
    if not is_admin(request.user):
        messages.error(request, "You don't have permission to access this page.")
        return HttpResponseForbidden("Access Denied")
    
    classrooms = Classroom.objects.all().order_by('-created_at')
    
    # Filter by status if specified
    status_filter = request.GET.get('status')
    if status_filter == 'active':
        classrooms = classrooms.filter(is_active=True, is_archived=False)
    elif status_filter == 'archived':
        classrooms = classrooms.filter(is_archived=True)
    elif status_filter == 'inactive':
        classrooms = classrooms.filter(is_active=False)
    
    context = {
        'classrooms': classrooms,
        'status_filter': status_filter,
    }
    
    return render(request, 'admin/classrooms.html', context)

@login_required
def admin_submissions(request):
    """
    Admin page to view and manage all submissions.
    """
    if not is_admin(request.user):
        messages.error(request, "You don't have permission to access this page.")
        return HttpResponseForbidden("Access Denied")
    
    submissions = AssignmentSubmission.objects.all().order_by('-submitted_at')
    
    # Filter by grading status if specified
    grading_filter = request.GET.get('grading')
    if grading_filter == 'graded':
        submissions = submissions.filter(is_graded=True)
    elif grading_filter == 'pending':
        submissions = submissions.filter(is_graded=False)
    
    # Filter by late status if specified
    late_filter = request.GET.get('late')
    if late_filter == 'late':
        submissions = submissions.filter(is_late=True)
    elif late_filter == 'on_time':
        submissions = submissions.filter(is_late=False)
    
    context = {
        'submissions': submissions,
        'grading_filter': grading_filter,
        'late_filter': late_filter,
    }
    
    return render(request, 'admin/submissions.html', context)
