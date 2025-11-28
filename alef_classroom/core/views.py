from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.db.models import Count
from classroom.models import Classroom, ClassroomMember
from assignment.models import Assignment, AssignmentSubmission

class HomeView(TemplateView):
    """View for the landing/home page of the application."""
    template_name = "base/home.html"

@login_required
def dashboard_view(request):
    """View for the user's dashboard with context data."""
    user = request.user
    
    # Get classroom statistics
    if user.is_teacher or user.is_admin:
        # Teachers and admins see classes they created
        classroom_count = Classroom.objects.filter(creator=user).count()
        assignment_count = Assignment.objects.filter(created_by=user).count()
    else:
        classroom_count = ClassroomMember.objects.filter(user=user).count()
        # Count pending assignments for students
        classrooms = ClassroomMember.objects.filter(user=user).values_list('classroom', flat=True)
        assignments = Assignment.objects.filter(classroom__in=classrooms, is_published=True)
        submissions = AssignmentSubmission.objects.filter(student=user).values_list('assignment', flat=True)
        assignment_count = assignments.exclude(id__in=submissions).count()
    
    # Get recent classrooms
    if user.is_teacher or user.is_admin:
        recent_classrooms = Classroom.objects.filter(creator=user).order_by('-created_at')[:5]
    else:
        memberships = ClassroomMember.objects.filter(user=user).select_related('classroom').order_by('-joined_at')[:5]
        recent_classrooms = [membership.classroom for membership in memberships]
    
    # Get recent activity
    activities = []
    if user.is_teacher or user.is_admin:
        # Recent submissions for teacher's assignments
        recent_submissions = AssignmentSubmission.objects.filter(
            assignment__created_by=user
        ).select_related('student', 'assignment').order_by('-submitted_at')[:10]
        
        for submission in recent_submissions:
            student_name = submission.student.get_full_name() or submission.student.username
            if submission.is_graded:
                description = f"{student_name} received {submission.points_earned}/{submission.assignment.points_possible} on {submission.assignment.title}"
                timestamp = submission.graded_at
            else:
                description = f"{student_name} submitted {submission.assignment.title} {'(late)' if submission.is_late else ''}"
                timestamp = submission.submitted_at
            
            activities.append({
                'type': 'submission',
                'title': f"{'Graded' if submission.is_graded else 'Submitted'}: {submission.assignment.title}",
                'user': student_name,
                'timestamp': timestamp,
                'description': description
            })
    else:
        # Recent assignments and grades for students
        classrooms = ClassroomMember.objects.filter(user=user).values_list('classroom', flat=True)
        
        # Get recent assignments
        recent_assignments = Assignment.objects.filter(
            classroom__in=classrooms,
            is_published=True
        ).order_by('-created_at')[:5]
        
        for assignment in recent_assignments:
            teacher_name = assignment.created_by.get_full_name() or assignment.created_by.username
            activities.append({
                'type': 'assignment',
                'title': f"New assignment: {assignment.title}",
                'user': teacher_name,
                'timestamp': assignment.created_at,
                'description': f"New assignment in {assignment.classroom.name}"
            })
        
        # Get recent grades
        recent_grades = AssignmentSubmission.objects.filter(
            student=user,
            is_graded=True
        ).select_related('assignment').order_by('-graded_at')[:5]
        
        for submission in recent_grades:
            teacher_name = submission.assignment.created_by.get_full_name() or submission.assignment.created_by.username
            activities.append({
                'type': 'grade',
                'title': f"Graded: {submission.assignment.title}",
                'user': teacher_name,
                'timestamp': submission.graded_at,
                'description': f"You received {submission.points_earned}/{submission.assignment.points_possible} on {submission.assignment.title}"
            })
    
    # Sort all activities by timestamp
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    activities = activities[:10]  # Limit to 10 items
    
    context = {
        'classroom_count': classroom_count,
        'assignment_count': assignment_count,
        'recent_classrooms': recent_classrooms,
        'activities': activities,
    }
    
    return render(request, 'base/dashboard.html', context)

# HTMX endpoints for dashboard statistics
@login_required
def dashboard_classroom_stats(request):
    """HTMX endpoint for classroom statistics."""
    user = request.user
    if user.is_teacher or user.is_admin:
        count = Classroom.objects.filter(creator=user).count()
    else:
        count = 0
    return HttpResponse(f"{count}")

@login_required
def dashboard_enrolled_stats(request):
    """HTMX endpoint for student enrollment statistics."""
    user = request.user
    count = ClassroomMember.objects.filter(user=user).count()
    return HttpResponse(f"{count}")

@login_required
def dashboard_assignment_stats(request):
    """HTMX endpoint for assignment statistics for teachers."""
    user = request.user
    if user.is_teacher or user.is_admin:
        count = Assignment.objects.filter(created_by=user).count()
    else:
        count = 0
    return HttpResponse(f"{count}")

@login_required
def dashboard_pending_stats(request):
    """HTMX endpoint for pending assignment statistics for students."""
    user = request.user
    if not user.is_teacher:
        # Count assignments not yet submitted
        classrooms = ClassroomMember.objects.filter(user=user).values_list('classroom', flat=True)
        assignments = Assignment.objects.filter(classroom__in=classrooms, is_published=True)
        submissions = AssignmentSubmission.objects.filter(student=user).values_list('assignment', flat=True)
        count = assignments.exclude(id__in=submissions).count()
    else:
        count = 0
    return HttpResponse(f"{count}")


@login_required
def dashboard_recent_classes(request):
    """HTMX endpoint for recent classes."""
    user = request.user
    
    if user.is_teacher or user.is_admin:
        classrooms = Classroom.objects.filter(creator=user).order_by('-created_at')[:5]
    else:
        memberships = ClassroomMember.objects.filter(user=user).select_related('classroom').order_by('-joined_at')[:5]
        classrooms = [membership.classroom for membership in memberships]
    
    return render(request, 'dashboard/recent_classes.html', {'classrooms': classrooms})

@login_required
def dashboard_recent_activity(request):
    """HTMX endpoint for recent activity."""
    user = request.user
    
    # This would be a more complex query in a real application
    # For now, we'll create a simple representation
    activities = []
    
    if user.is_teacher or user.is_admin:
        # Recent submissions for teacher's/admin's assignments
        recent_submissions = AssignmentSubmission.objects.filter(
            assignment__created_by=user
        ).select_related('student', 'assignment').order_by('-submitted_at')[:10]
        
        for submission in recent_submissions:
            activities.append({
                'type': 'submission',
                'title': f"Submission: {submission.assignment.title}",
                'user': submission.student.username,
                'timestamp': submission.submitted_at,
                'description': f"Submitted {'late' if submission.is_late else 'on time'}"
            })
            
    else:
        # Recent assignments for students
        classrooms = ClassroomMember.objects.filter(user=user).values_list('classroom', flat=True)
        
        recent_assignments = Assignment.objects.filter(
            classroom__in=classrooms,
            is_published=True
        ).order_by('-created_at')[:5]
        
        for assignment in recent_assignments:
            activities.append({
                'type': 'assignment',
                'title': assignment.title,
                'user': assignment.created_by.username,
                'timestamp': assignment.created_at,
                'description': f"New assignment in {assignment.classroom.name}"
            })
    
    # Sort all activities by timestamp
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    activities = activities[:10]  # Limit to 10 items
    
    return render(request, 'dashboard/recent_activity.html', {'activities': activities})
