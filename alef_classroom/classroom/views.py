from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator

from .models import Classroom, ClassroomMember, Announcement, Comment
from .forms import ClassroomForm, ClassroomJoinForm, AnnouncementForm, CommentForm
from accounts.models import User

@login_required
def classroom_list(request):
    """
    Display a list of classrooms the user is enrolled in or has created.
    Admins can see all classrooms.
    """
    # Admins can see all classrooms
    if request.user.is_admin:
        all_classrooms = Classroom.objects.filter(is_active=True).order_by('-created_at')
        teaching_classrooms = all_classrooms
        enrolled_classrooms = []
    else:
        # Get classrooms where the user is a member
        enrollments = ClassroomMember.objects.filter(user=request.user, is_active=True)
        enrolled_classrooms = [enrollment.classroom for enrollment in enrollments]
        
        # Get classrooms created by the user that they might not be a member of
        created_classrooms = Classroom.objects.filter(creator=request.user, is_active=True)
        
        # Combine and remove duplicates
        all_classrooms = list(set(enrolled_classrooms + list(created_classrooms)))
        
        # Sort by creation date (newest first)
        all_classrooms.sort(key=lambda x: x.created_at, reverse=True)
        
        # Split into teaching and enrolled classes
        teaching_classrooms = []
        enrolled_classrooms = []
        
        for classroom in all_classrooms:
            # The creator is always considered a teacher
            if classroom.creator == request.user:
                teaching_classrooms.append(classroom)
            else:
                # Check if the user is a teacher in this classroom
                try:
                    membership = ClassroomMember.objects.get(classroom=classroom, user=request.user)
                    if membership.role == ClassroomMember.Role.TEACHER:
                        teaching_classrooms.append(classroom)
                    else:
                        enrolled_classrooms.append(classroom)
                except ClassroomMember.DoesNotExist:
                    # This shouldn't happen, but just in case
                    pass
    
    # Form for joining a classroom
    join_form = ClassroomJoinForm()
    
    context = {
        'teaching_classrooms': teaching_classrooms,
        'enrolled_classrooms': enrolled_classrooms,
        'join_form': join_form,
    }
    
    return render(request, 'classroom/list.html', context)

@login_required
def classroom_create(request):
    """
    Create a new classroom.
    Only teachers and admins can create classrooms.
    """
    # Restrict creation to teachers and admins only
    if not (request.user.is_teacher or request.user.is_admin):
        messages.error(request, "Only teachers and administrators can create classrooms.")
        return HttpResponseForbidden("You don't have permission to create classrooms.")
    
    if request.method == 'POST':
        form = ClassroomForm(request.POST, request.FILES)
        if form.is_valid():
            classroom = form.save(commit=False)
            classroom.creator = request.user
            classroom.save()
            
            # Add the creator as a teacher member
            ClassroomMember.objects.create(
                classroom=classroom,
                user=request.user,
                role=ClassroomMember.Role.TEACHER
            )
            
            messages.success(request, "Classroom created successfully!")
            return redirect('classroom:detail', pk=classroom.pk)
    else:
        form = ClassroomForm()
    
    return render(request, 'classroom/create.html', {'form': form})

@login_required
def classroom_detail(request, pk):
    """
    Display a classroom and its announcements.
    """
    classroom = get_object_or_404(Classroom, pk=pk, is_active=True)
    
    # Check if the user is a member of this classroom
    try:
        membership = ClassroomMember.objects.get(classroom=classroom, user=request.user)
        is_member = True
        is_teacher = membership.role in [ClassroomMember.Role.TEACHER, ClassroomMember.Role.ADMIN]
    except ClassroomMember.DoesNotExist:
        # User is not a member, but might be the creator or an admin
        is_member = classroom.creator == request.user or request.user.is_admin
        is_teacher = is_member  # Creator and admins are considered teachers
    
    if not is_member:
        return render(request, 'classroom/join_required.html', {'classroom': classroom})
    
    # Get announcements for this classroom
    announcements = Announcement.objects.filter(classroom=classroom)
    
    # Form for creating new announcements (only for teachers)
    announcement_form = AnnouncementForm() if is_teacher else None
    
    # Get all members of the classroom, separated by role
    members = ClassroomMember.objects.filter(classroom=classroom)
    teachers = members.filter(role=ClassroomMember.Role.TEACHER)
    students = members.filter(role=ClassroomMember.Role.STUDENT)
    admins = members.filter(role=ClassroomMember.Role.ADMIN)
    
    context = {
        'classroom': classroom,
        'announcements': announcements,
        'announcement_form': announcement_form,
        'is_teacher': is_teacher,
        'teachers': teachers,
        'students': students,
        'admins': admins,
        'comment_form': CommentForm(),
    }
    
    return render(request, 'classroom/detail.html', context)

@login_required
def classroom_edit(request, pk):
    """
    Edit an existing classroom.
    """
    classroom = get_object_or_404(Classroom, pk=pk)
    
    # Only the creator or teachers can edit the classroom
    if request.user != classroom.creator and not ClassroomMember.objects.filter(
        classroom=classroom, user=request.user, role=ClassroomMember.Role.TEACHER
    ).exists():
        return HttpResponseForbidden("You don't have permission to edit this classroom.")
    
    if request.method == 'POST':
        form = ClassroomForm(request.POST, request.FILES, instance=classroom)
        if form.is_valid():
            form.save()
            messages.success(request, "Classroom updated successfully!")
            return redirect('classroom:detail', pk=classroom.pk)
    else:
        form = ClassroomForm(instance=classroom)
    
    return render(request, 'classroom/edit.html', {'form': form, 'classroom': classroom})

@login_required
def classroom_delete(request, pk):
    """
    Delete a classroom.
    """
    classroom = get_object_or_404(Classroom, pk=pk)
    
    # Only the creator can delete the classroom
    if request.user != classroom.creator:
        return HttpResponseForbidden("You don't have permission to delete this classroom.")
    
    if request.method == 'POST':
        classroom.is_active = False
        classroom.save()
        messages.success(request, "Classroom deleted successfully!")
        return redirect('classroom:list')
    
    return render(request, 'classroom/delete.html', {'classroom': classroom})

@login_required
def classroom_join(request, pk=None):
    """
    Join a classroom using a course code or by direct link.
    """
    # If a pk is provided, it's a direct join link
    if pk:
        classroom = get_object_or_404(Classroom, pk=pk, is_active=True)
        
        # Check if already a member
        if ClassroomMember.objects.filter(classroom=classroom, user=request.user).exists():
            messages.info(request, "You are already a member of this classroom.")
            return redirect('classroom:detail', pk=classroom.pk)
        
        # Join with appropriate role based on user's account role
        if request.user.is_admin:
            role = ClassroomMember.Role.ADMIN
        elif request.user.is_teacher:
            role = ClassroomMember.Role.TEACHER
        else:
            role = ClassroomMember.Role.STUDENT
        
        ClassroomMember.objects.create(
            classroom=classroom,
            user=request.user,
            role=role
        )
        
        messages.success(request, f"You have joined {classroom.name}!")
        return redirect('classroom:detail', pk=classroom.pk)
    
    # Otherwise, use the form to join by course code
    if request.method == 'POST':
        form = ClassroomJoinForm(request.POST)
        if form.is_valid():
            course_code = form.cleaned_data['course_code']
            
            # Try case-insensitive matching (course_code is cleaned by form - whitespace stripped)
            try:
                # Try case-insensitive match (SQLite supports this)
                classroom = Classroom.objects.get(course_code__iexact=course_code, is_active=True)
            except Classroom.DoesNotExist:
                # If case-insensitive doesn't work, try exact match
                try:
                    classroom = Classroom.objects.get(course_code=course_code, is_active=True)
                except Classroom.DoesNotExist:
                    messages.error(request, "Invalid course code. Please try again.")
                    return redirect('classroom:list')
            
            # Check if already a member
            if ClassroomMember.objects.filter(classroom=classroom, user=request.user).exists():
                messages.info(request, "You are already a member of this classroom.")
                return redirect('classroom:detail', pk=classroom.pk)
            
            # Join with appropriate role based on user's account role
            if request.user.is_admin:
                role = ClassroomMember.Role.ADMIN
            elif request.user.is_teacher:
                role = ClassroomMember.Role.TEACHER
            else:
                role = ClassroomMember.Role.STUDENT
            
            ClassroomMember.objects.create(
                classroom=classroom,
                user=request.user,
                role=role
            )
            
            messages.success(request, f"You have joined {classroom.name}!")
            return redirect('classroom:detail', pk=classroom.pk)
    
    return redirect('classroom:list')

@login_required
def announcement_create(request, classroom_pk):
    """
    Create a new announcement in a classroom.
    """
    classroom = get_object_or_404(Classroom, pk=classroom_pk, is_active=True)
    
    # Check if the user is a teacher in this classroom
    is_teacher = classroom.creator == request.user or ClassroomMember.objects.filter(
        classroom=classroom, user=request.user, role=ClassroomMember.Role.TEACHER
    ).exists()
    
    if not is_teacher:
        return HttpResponseForbidden("Only teachers can post announcements.")
    
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.classroom = classroom
            announcement.author = request.user
            announcement.save()
            
            messages.success(request, "Announcement posted successfully!")
            return redirect('classroom:detail', pk=classroom.pk)
    
    return redirect('classroom:detail', pk=classroom.pk)

@login_required
def comment_create(request, announcement_pk):
    """
    Create a new comment on an announcement.
    """
    announcement = get_object_or_404(Announcement, pk=announcement_pk)
    classroom = announcement.classroom
    
    # Check if the user is a member of this classroom
    is_member = classroom.creator == request.user or ClassroomMember.objects.filter(
        classroom=classroom, user=request.user
    ).exists()
    
    if not is_member:
        return HttpResponseForbidden("You must be a member of this classroom to comment.")
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.announcement = announcement
            comment.author = request.user
            comment.save()
            
            messages.success(request, "Comment added successfully!")
    
    return redirect('classroom:detail', pk=classroom.pk)
