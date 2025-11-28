from django.contrib import admin
from .models import Classroom, ClassroomMember, Announcement, Comment

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    """
    Admin for classrooms - allows viewing and managing all classrooms.
    """
    list_display = ('name', 'creator', 'subject', 'section', 'course_code', 'is_active', 'created_at')
    list_filter = ('is_active', 'is_archived', 'created_at', 'subject')
    search_fields = ('name', 'description', 'course_code', 'creator__username')
    readonly_fields = ('course_code', 'slug', 'created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'subject', 'section')
        }),
        ('Course Details', {
            'fields': ('course_code', 'slug', 'creator', 'banner_image')
        }),
        ('Status', {
            'fields': ('is_active', 'is_archived')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-created_at',)


@admin.register(ClassroomMember)
class ClassroomMemberAdmin(admin.ModelAdmin):
    """
    Admin for classroom members - allows managing user roles in classrooms.
    """
    list_display = ('user', 'classroom', 'role', 'is_active', 'joined_at')
    list_filter = ('role', 'is_active', 'classroom', 'joined_at')
    search_fields = ('user__username', 'classroom__name')
    readonly_fields = ('joined_at', 'last_active')
    fieldsets = (
        ('Member Information', {
            'fields': ('user', 'classroom', 'role')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Activity', {
            'fields': ('joined_at', 'last_active'),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-joined_at',)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    """
    Admin for announcements - allows viewing and managing all announcements.
    """
    list_display = ('title', 'classroom', 'author', 'is_pinned', 'created_at')
    list_filter = ('is_pinned', 'classroom', 'created_at')
    search_fields = ('title', 'content', 'classroom__name', 'author__username')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Announcement Details', {
            'fields': ('title', 'content', 'classroom', 'author')
        }),
        ('Options', {
            'fields': ('is_pinned',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-created_at',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin for comments - allows viewing and managing all comments.
    """
    list_display = ('author', 'announcement', 'created_at')
    list_filter = ('announcement', 'created_at')
    search_fields = ('content', 'author__username', 'announcement__title')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Comment Details', {
            'fields': ('content', 'author', 'announcement')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-created_at',)
