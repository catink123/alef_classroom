from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from django.utils import timezone
from .models import Assignment, AssignmentSubmission, Comment
from classroom.models import Classroom, ClassroomMember
from django.db.models import Q

# Helper function to check if user is a teacher or admin in a classroom
def is_teacher(user, classroom):
    # Admins can always act as teachers
    if user.is_admin:
        return True
    try:
        member = ClassroomMember.objects.get(user=user, classroom=classroom)
        return member.role in [ClassroomMember.Role.TEACHER, ClassroomMember.Role.ADMIN]
    except ClassroomMember.DoesNotExist:
        # Check if user is the creator (always considered a teacher)
        return classroom.creator == user

# Helper function to check if user is a student in a classroom
def is_student(user, classroom):
    try:
        member = ClassroomMember.objects.get(user=user, classroom=classroom)
        return member.role == ClassroomMember.Role.STUDENT
    except ClassroomMember.DoesNotExist:
        return False

# Helper function to check if user is a member of a classroom
def is_classroom_member(user, classroom):
    return ClassroomMember.objects.filter(user=user, classroom=classroom).exists()

# Assignment Views
@login_required
def assignment_list(request, classroom_slug):
    classroom = get_object_or_404(Classroom, slug=classroom_slug)
    
    # Admins can view all classrooms and assignments
    if not request.user.is_admin:
        # Check if user is a member of the classroom
        if not is_classroom_member(request.user, classroom):
            messages.error(request, "You are not a member of this classroom.")
            return redirect('classroom:list')
    
    # Get assignments for this classroom
    assignments = Assignment.objects.filter(classroom=classroom)
    
    # For students, show only published assignments
    if not is_teacher(request.user, classroom):
        assignments = assignments.filter(is_published=True, is_draft=False)
    
    # For students, include submission status
    if is_student(request.user, classroom):
        for assignment in assignments:
            try:
                submission = AssignmentSubmission.objects.get(
                    assignment=assignment,
                    student=request.user
                )
                assignment.user_submission = submission
            except AssignmentSubmission.DoesNotExist:
                assignment.user_submission = None
    
    context = {
        'classroom': classroom,
        'assignments': assignments,
        'is_teacher': is_teacher(request.user, classroom)
    }
    
    return render(request, 'assignment/list.html', context)

@login_required
def assignment_create(request, classroom_slug):
    classroom = get_object_or_404(Classroom, slug=classroom_slug)
    
    # Check if user is a teacher
    if not is_teacher(request.user, classroom):
        messages.error(request, "Only teachers can create assignments.")
        return redirect('classroom:detail', pk=classroom.pk)
    
    # Handle form submission
    if request.method == 'POST':
        # Process form data
        title = request.POST.get('title')
        description = request.POST.get('description')
        instructions = request.POST.get('instructions')
        due_date = request.POST.get('due_date')
        points_possible = request.POST.get('points_possible', 100)
        is_published = 'is_published' in request.POST
        is_draft = 'is_draft' in request.POST
        allow_late = 'allow_late' in request.POST
        late_penalty = request.POST.get('late_penalty', 0)
        
        # Create new assignment
        assignment = Assignment.objects.create(
            title=title,
            description=description,
            instructions=instructions,
            classroom=classroom,
            created_by=request.user,
            due_date=due_date,
            points_possible=points_possible,
            is_published=is_published,
            is_draft=is_draft,
            allow_late_submissions=allow_late,
            late_penalty_percentage=late_penalty
        )
        
        # Handle file upload
        if 'attachment' in request.FILES:
            assignment.attachment = request.FILES['attachment']
            assignment.save()
        
        messages.success(request, "Assignment created successfully!")
        return redirect('assignment:detail', pk=assignment.id)
    
    context = {
        'classroom': classroom
    }
    
    return render(request, 'assignment/create.html', context)

@login_required
def assignment_edit(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    classroom = assignment.classroom
    
    # Check if user is a teacher and created this assignment
    if not is_teacher(request.user, classroom) or assignment.created_by != request.user:
        messages.error(request, "You don't have permission to edit this assignment.")
        return redirect('assignment:detail', pk=assignment.id)
    
    # Handle form submission
    if request.method == 'POST':
        # Update assignment fields
        assignment.title = request.POST.get('title')
        assignment.description = request.POST.get('description')
        assignment.instructions = request.POST.get('instructions')
        assignment.due_date = request.POST.get('due_date')
        assignment.points_possible = request.POST.get('points_possible', 100)
        assignment.is_published = 'is_published' in request.POST
        assignment.is_draft = 'is_draft' in request.POST
        assignment.allow_late_submissions = 'allow_late' in request.POST
        assignment.late_penalty_percentage = request.POST.get('late_penalty', 0)
        
        # Handle file upload
        if 'attachment' in request.FILES:
            assignment.attachment = request.FILES['attachment']
        
        assignment.save()
        messages.success(request, "Assignment updated successfully!")
        return redirect('assignment:detail', pk=assignment.id)
    
    context = {
        'assignment': assignment,
        'classroom': classroom
    }
    
    return render(request, 'assignment/edit.html', context)

@login_required
def assignment_delete(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    classroom = assignment.classroom
    
    # Check if user is a teacher and created this assignment
    if not is_teacher(request.user, classroom) or assignment.created_by != request.user:
        messages.error(request, "You don't have permission to delete this assignment.")
        return redirect('assignment:detail', pk=assignment.id)
    
    if request.method == 'POST':
        classroom_slug = classroom.slug
        assignment.delete()
        messages.success(request, "Assignment deleted successfully!")
        return redirect('assignment:list', classroom_slug=classroom_slug)
    
    context = {
        'assignment': assignment
    }
    
    return render(request, 'assignment/delete.html', context)

@login_required
def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    classroom = assignment.classroom
    
    # Check if user is a member of the classroom
    if not is_classroom_member(request.user, classroom):
        messages.error(request, "You are not a member of this classroom.")
        return redirect('classroom:list')
    
    # Students can only view published assignments
    if is_student(request.user, classroom) and (not assignment.is_published or assignment.is_draft):
        messages.error(request, "This assignment is not available.")
        return redirect('assignment:list', classroom_slug=classroom.slug)
    
    # Get user's submission if exists
    user_submission = None
    if is_student(request.user, classroom):
        try:
            user_submission = AssignmentSubmission.objects.get(
                assignment=assignment,
                student=request.user
            )
        except AssignmentSubmission.DoesNotExist:
            pass
    
    # Get comments
    comments = Comment.objects.filter(assignment=assignment)
    
    context = {
        'assignment': assignment,
        'classroom': classroom,
        'is_teacher': is_teacher(request.user, classroom),
        'user_submission': user_submission,
        'comments': comments,
        'now': timezone.now()
    }
    
    return render(request, 'assignment/detail.html', context)

# Submission Views
@login_required
def submission_create(request, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    classroom = assignment.classroom
    
    # Check if user is a student
    if not is_student(request.user, classroom):
        messages.error(request, "Only students can submit assignments.")
        return redirect('assignment:detail', pk=assignment.id)
    
    # Check if assignment is available for submission
    if not assignment.is_published or assignment.is_draft:
        messages.error(request, "This assignment is not available for submission.")
        return redirect('assignment:list', classroom_slug=classroom.slug)
    
    # Check if student already submitted
    try:
        existing_submission = AssignmentSubmission.objects.get(
            assignment=assignment,
            student=request.user
        )
        return redirect('assignment:edit_submission', pk=existing_submission.id)
    except AssignmentSubmission.DoesNotExist:
        pass
    
    # Check if submission is late
    is_late = timezone.now() > assignment.due_date
    
    # If late submissions are not allowed
    if is_late and not assignment.allow_late_submissions:
        messages.error(request, "The deadline for this assignment has passed.")
        return redirect('assignment:detail', pk=assignment.id)
    
    if request.method == 'POST':
        content = request.POST.get('content', '')
        
        # Create submission
        submission = AssignmentSubmission.objects.create(
            assignment=assignment,
            student=request.user,
            content=content,
            is_late=is_late
        )
        
        # Handle file upload
        if 'attachment' in request.FILES:
            submission.attachment = request.FILES['attachment']
            submission.save()
        
        messages.success(request, "Assignment submitted successfully!")
        return redirect('assignment:detail', pk=assignment.id)
    
    context = {
        'assignment': assignment,
        'is_late': is_late
    }
    
    return render(request, 'assignment/submit.html', context)

@login_required
def submission_edit(request, pk):
    submission = get_object_or_404(AssignmentSubmission, pk=pk)
    assignment = submission.assignment
    classroom = assignment.classroom
    
    # Check if user is the owner of the submission
    if submission.student != request.user:
        messages.error(request, "You don't have permission to edit this submission.")
        return redirect('assignment:detail', pk=assignment.id)
    
    # Check if submission is already graded
    if submission.is_graded:
        messages.error(request, "You cannot edit a submission that has been graded.")
        return redirect('assignment:detail', pk=assignment.id)
    
    if request.method == 'POST':
        submission.content = request.POST.get('content', '')
        
        # Handle file upload
        if 'attachment' in request.FILES:
            submission.attachment = request.FILES['attachment']
        
        submission.save()
        messages.success(request, "Submission updated successfully!")
        return redirect('assignment:detail', pk=assignment.id)
    
    context = {
        'submission': submission,
        'assignment': assignment
    }
    
    return render(request, 'assignment/edit_submission.html', context)

@login_required
def submission_list(request, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    classroom = assignment.classroom
    
    # Check if user is a teacher
    if not is_teacher(request.user, classroom):
        messages.error(request, "Only teachers can view all submissions.")
        return redirect('assignment:detail', pk=assignment.id)
    
    submissions = AssignmentSubmission.objects.filter(assignment=assignment)
    
    context = {
        'assignment': assignment,
        'classroom': classroom,
        'submissions': submissions
    }
    
    return render(request, 'assignment/submissions.html', context)

@login_required
def submission_detail(request, pk):
    submission = get_object_or_404(AssignmentSubmission, pk=pk)
    assignment = submission.assignment
    classroom = assignment.classroom
    
    # Check if user is a teacher or the owner of the submission
    if not (is_teacher(request.user, classroom) or submission.student == request.user):
        messages.error(request, "You don't have permission to view this submission.")
        return redirect('assignment:detail', pk=assignment.id)
    
    # Get comments
    comments = Comment.objects.filter(submission=submission)
    
    context = {
        'submission': submission,
        'assignment': assignment,
        'classroom': classroom,
        'is_teacher': is_teacher(request.user, classroom),
        'comments': comments
    }
    
    return render(request, 'assignment/submission_detail.html', context)

@login_required
def submission_grade(request, pk):
    submission = get_object_or_404(AssignmentSubmission, pk=pk)
    assignment = submission.assignment
    classroom = assignment.classroom
    
    # Check if user is a teacher
    if not is_teacher(request.user, classroom):
        messages.error(request, "Only teachers can grade submissions.")
        return redirect('assignment:detail', pk=assignment.id)
    
    if request.method == 'POST':
        points = request.POST.get('points')
        feedback = request.POST.get('feedback', '')
        
        try:
            points = float(points)
            if points < 0 or points > assignment.points_possible:
                raise ValueError
        except ValueError:
            messages.error(request, "Please enter a valid point value.")
            return redirect('assignment:submission_detail', pk=submission.id)
        
        submission.points_earned = points
        submission.feedback = feedback
        submission.is_graded = True
        submission.graded_by = request.user
        submission.graded_at = timezone.now()
        submission.save()
        
        messages.success(request, "Submission graded successfully!")
        return redirect('assignment:submission_detail', pk=submission.id)
    
    context = {
        'submission': submission,
        'assignment': assignment
    }
    
    return render(request, 'assignment/grade.html', context)

# Comment Views
@login_required
def assignment_comment(request, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    classroom = assignment.classroom
    
    # Check if user is a member of the classroom
    if not is_classroom_member(request.user, classroom):
        messages.error(request, "You are not a member of this classroom.")
        return redirect('classroom:list')
    
    if request.method == 'POST':
        content = request.POST.get('content')
        
        if not content:
            messages.error(request, "Comment cannot be empty.")
            return redirect('assignment:detail', pk=assignment.id)
        
        Comment.objects.create(
            content=content,
            author=request.user,
            assignment=assignment
        )
        
        messages.success(request, "Comment added successfully!")
    
    return redirect('assignment:detail', pk=assignment.id)

@login_required
def submission_comment(request, submission_id):
    submission = get_object_or_404(AssignmentSubmission, pk=submission_id)
    assignment = submission.assignment
    classroom = assignment.classroom
    
    # Check if user is a teacher or the owner of the submission
    if not (is_teacher(request.user, classroom) or submission.student == request.user):
        messages.error(request, "You don't have permission to comment on this submission.")
        return redirect('assignment:detail', pk=assignment.id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        
        if not content:
            messages.error(request, "Comment cannot be empty.")
            return redirect('assignment:submission_detail', pk=submission.id)
        
        Comment.objects.create(
            content=content,
            author=request.user,
            submission=submission
        )
        
        messages.success(request, "Comment added successfully!")
    
    return redirect('assignment:submission_detail', pk=submission.id)
