from django.contrib import admin
from .models import StudyGroup, GroupMember, GroupInvitation, ChatMessage, SharedResource, Assignment, Submission, PeerReview

@admin.register(StudyGroup)
class StudyGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'creator', 'visibility', 'member_count', 'created_at']
    list_filter = ['visibility', 'created_at']
    search_fields = ['name', 'description']

@admin.register(GroupMember)
class GroupMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'group', 'role', 'joined_at']
    list_filter = ['role', 'joined_at']

@admin.register(GroupInvitation)
class GroupInvitationAdmin(admin.ModelAdmin):
    list_display = ['group', 'invited_user', 'invited_by', 'is_accepted', 'created_at']
    list_filter = ['is_accepted', 'created_at']

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'group', 'message_type', 'created_at']
    list_filter = ['message_type', 'created_at']

@admin.register(SharedResource)
class SharedResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'group', 'uploaded_by', 'resource_type', 'download_count', 'created_at']
    list_filter = ['resource_type', 'created_at']

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'group', 'created_by', 'due_date', 'max_points']
    list_filter = ['due_date', 'created_at']

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'assignment', 'submitted_at', 'is_late', 'points']
    list_filter = ['is_late', 'submitted_at']

@admin.register(PeerReview)
class PeerReviewAdmin(admin.ModelAdmin):
    list_display = ['reviewer', 'submission', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']