from django.db import models
from django.urls import reverse
from accounts.models import User
from django.utils.text import slugify
import markdown
from django.utils.html import strip_tags

class NoteCategory(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#3B82F6')
    icon = models.CharField(max_length=50, default='📝')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='note_categories')
    
    class Meta:
        verbose_name_plural = "Note categories"
        unique_together = ['name', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"

class Note(models.Model):
    NOTE_TYPES = (
        ('text', 'Text Note'),
        ('code', 'Code Snippet'),
        ('math', 'Math Formula'),
        ('diagram', 'Diagram'),
    )
    
    VISIBILITY_CHOICES = (
        ('private', 'Private'),
        ('shared', 'Shared with link'),
        ('public', 'Public'),
    )
    
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    content_html = models.TextField(blank=True)  # Rendered HTML
    summary = models.TextField(blank=True)  # AI-generated summary
    note_type = models.CharField(max_length=20, choices=NOTE_TYPES, default='text')
    category = models.ForeignKey(NoteCategory, on_delete=models.SET_NULL, 
                               null=True, blank=True, related_name='notes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    
    # Metadata
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='private')
    is_pinned = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    word_count = models.IntegerField(default=0)
    reading_time = models.IntegerField(default=0)  # in minutes
    
    # AI Features
    ai_summary_generated = models.BooleanField(default=False)
    key_points = models.JSONField(default=list, blank=True)  # Store AI-extracted key points
    related_concepts = models.JSONField(default=list, blank=True)  # AI-suggested concepts
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_accessed = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_pinned', '-updated_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('notes:note_detail', kwargs={'pk': self.pk})
    
    def save(self, *args, **kwargs):
        # Convert markdown to HTML
        if self.content:
            self.content_html = markdown.markdown(self.content)
            # Calculate word count (rough estimate)
            plain_text = strip_tags(self.content_html)
            self.word_count = len(plain_text.split())
            self.reading_time = max(1, self.word_count // 200)  # 200 wpm
        super().save(*args, **kwargs)
    
    @property
    def preview(self):
        """Return a short preview of the content"""
        if self.summary:
            return self.summary[:150] + '...' if len(self.summary) > 150 else self.summary
        plain_text = strip_tags(self.content_html)
        return plain_text[:150] + '...' if len(plain_text) > 150 else plain_text

class NoteTag(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default='#6B7280')
    notes = models.ManyToManyField(Note, related_name='tags', blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='note_tags')
    
    class Meta:
        unique_together = ['name', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"

class NoteVersion(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='versions')
    content = models.TextField()
    version_number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-version_number']
        unique_together = ['note', 'version_number']
    
    def __str__(self):
        return f"{self.note.title} - v{self.version_number}"

class NoteCollaborator(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='collaborators')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    can_edit = models.BooleanField(default=True)
    added_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, 
                               related_name='added_collaborators')
    
    class Meta:
        unique_together = ['note', 'user']
    
    def __str__(self):
        return f"{self.user.username} -> {self.note.title}"