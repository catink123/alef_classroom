from django.contrib import admin
from .models import Assignment, AssignmentSubmission, Comment

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    """
    Admin for assignments - allows viewing and managing all assignments.
    """
    list_display = ('title', 'classroom', 'created_by', 'due_date', 'is_published', 'is_draft', 'submission_count', 'graded_count')
    list_filter = ('is_published', 'is_draft', 'classroom', 'created_at', 'due_date')
    search_fields = ('title', 'description', 'classroom__name', 'created_by__username')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'due_date'
    fieldsets = (
        ('Assignment Details', {
            'fields': ('title', 'description', 'instructions', 'classroom', 'created_by')
        }),
        ('Dates & Points', {
            'fields': ('due_date', 'points_possible')
        }),
        ('Submission Settings', {
            'fields': ('allow_late_submissions', 'late_penalty_percentage')
        }),
        ('Status', {
            'fields': ('is_published', 'is_draft')
        }),
        ('Attachment', {
            'fields': ('attachment',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-created_at',)

@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    """
    Admin for submissions - allows viewing and managing all submissions.
    """
    list_display = ('student', 'assignment', 'submitted_at', 'is_late', 'is_graded', 'points_earned', 'graded_by')
    list_filter = ('is_graded', 'is_late', 'assignment', 'submitted_at')
    search_fields = ('student__username', 'assignment__title', 'feedback')
    readonly_fields = ('submitted_at', 'updated_at', 'graded_at')
    date_hierarchy = 'submitted_at'
    fieldsets = (
        ('Submission Details', {
            'fields': ('assignment', 'student', 'content', 'attachment')
        }),
        ('Grading', {
            'fields': ('is_graded', 'points_earned', 'feedback', 'graded_by')
        }),
        ('Status', {
            'fields': ('is_late',)
        }),
        ('Timestamps', {
            'fields': ('submitted_at', 'updated_at', 'graded_at'),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-submitted_at',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin for assignment comments - allows viewing and managing all comments.
    """
    list_display = ('author', 'assignment', 'submission', 'created_at')
    list_filter = ('assignment', 'submission', 'created_at')
    search_fields = ('content', 'author__username')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Comment Details', {
            'fields': ('content', 'author')
        }),
        ('Related To', {
            'fields': ('assignment', 'submission')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-created_at',)
