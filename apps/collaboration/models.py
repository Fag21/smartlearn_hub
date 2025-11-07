from django.db import models
from django.urls import reverse
from accounts.models import User
from courses.models import Course

class StudyGroup(models.Model):
    VISIBILITY_CHOICES = (
        ('private', 'Private'),
        ('public', 'Public'),
    )
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, 
                             related_name='study_groups', null=True, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='private')
    max_members = models.IntegerField(default=10)
    
    # Group settings
    allow_join_requests = models.BooleanField(default=True)
    allow_member_invites = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('collaboration:study_group_detail', kwargs={'pk': self.pk})
    
    @property
    def member_count(self):
        return self.members.count()
    
    @property
    def is_full(self):
        return self.member_count >= self.max_members

class GroupMember(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
        ('member', 'Member'),
    )
    
    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['group', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.group.name}"

class GroupInvitation(models.Model):
    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='invitations')
    invited_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_invitations')
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations')
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)
    accepted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['group', 'invited_user']
    
    def __str__(self):
        return f"{self.group.name} -> {self.invited_user.username}"

class ChatMessage(models.Model):
    MESSAGE_TYPES = (
        ('text', 'Text'),
        ('system', 'System Message'),
        ('file', 'File Share'),
    )
    
    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    content = models.TextField()
    file = models.FileField(upload_to='group_chat_files/', blank=True, null=True)
    
    # Reply functionality
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, 
                               null=True, blank=True, related_name='replies')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.user.username}: {self.content[:50]}"

class SharedResource(models.Model):
    RESOURCE_TYPES = (
        ('note', 'Note'),
        ('file', 'File'),
        ('link', 'Link'),
        ('assignment', 'Assignment'),
    )
    
    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='resources')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_resources')
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES, default='file')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='group_resources/', blank=True, null=True)
    url = models.URLField(blank=True)
    # Reference to note from notes app
    note = models.ForeignKey('notes.Note', on_delete=models.CASCADE, 
                           null=True, blank=True, related_name='shared_in_groups')
    
    # Metadata
    download_count = models.IntegerField(default=0)
    is_pinned = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class Assignment(models.Model):
    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='assignments')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_assignments')
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()
    max_points = models.IntegerField(default=100)
    
    # Submission settings
    allow_late_submissions = models.BooleanField(default=False)
    allow_resubmissions = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.group.name} - {self.title}"

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignment_submissions')
    content = models.TextField()
    file = models.FileField(upload_to='assignment_submissions/', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_late = models.BooleanField(default=False)
    
    # Grading
    points = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    graded_by = models.ForeignKey(User, on_delete=models.SET_NULL, 
                                null=True, blank=True, related_name='graded_submissions')
    graded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['assignment', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.assignment.title}"

class PeerReview(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='peer_reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    rating = models.IntegerField(help_text="Rating from 1-5")
    comments = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['submission', 'reviewer']
    
    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.submission.user.username}"