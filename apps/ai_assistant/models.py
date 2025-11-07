from django.db import models
from accounts.models import User
from courses.models import Course, Lesson
from notes.models import Note

class AIConversation(models.Model):
    CONVERSATION_TYPES = (
        ('study_help', 'Study Help'),
        ('content_explanation', 'Content Explanation'),
        ('quiz_prep', 'Quiz Preparation'),
        ('career_advice', 'Career Advice'),
        ('general', 'General'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_conversations')
    title = models.CharField(max_length=200)
    conversation_type = models.CharField(max_length=50, choices=CONVERSATION_TYPES, default='general')
    context_course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    context_lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True)
    context_note = models.ForeignKey(Note, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"

class AIMessage(models.Model):
    MESSAGE_TYPES = (
        ('user', 'User'),
        ('assistant', 'AI Assistant'),
        ('system', 'System'),
    )
    
    conversation = models.ForeignKey(AIConversation, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)
    content = models.TextField()
    tokens_used = models.IntegerField(default=0)
    processing_time = models.FloatField(default=0.0)  # in seconds
    
    # For context-aware responses
    referenced_content = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.message_type}: {self.content[:50]}..."

class AIRecommendation(models.Model):
    RECOMMENDATION_TYPES = (
        ('course', 'Course'),
        ('lesson', 'Lesson'),
        ('resource', 'Resource'),
        ('study_technique', 'Study Technique'),
        ('career_path', 'Career Path'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_recommendations')
    recommendation_type = models.CharField(max_length=50, choices=RECOMMENDATION_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    reasoning = models.TextField(blank=True)  # AI's reasoning for this recommendation
    
    # Target content
    target_course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    target_lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, blank=True)
    external_url = models.URLField(blank=True)
    
    # Scoring
    confidence_score = models.FloatField(default=0.0)  # 0-1 scale
    relevance_score = models.FloatField(default=0.0)   # 0-1 scale
    
    # User feedback
    is_accepted = models.BooleanField(default=False)
    user_feedback = models.CharField(max_length=20, blank=True, choices=(
        ('helpful', 'Helpful'),
        ('not_helpful', 'Not Helpful'),
        ('already_know', 'Already Know'),
    ))
    
    created_at = models.DateTimeField(auto_now_add=True)
    shown_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-confidence_score', '-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"

class LearningPattern(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='learning_pattern')
    
    # Learning preferences
    preferred_learning_style = models.CharField(max_length=50, blank=True, choices=(
        ('visual', 'Visual'),
        ('auditory', 'Auditory'),
        ('kinesthetic', 'Kinesthetic'),
        ('reading_writing', 'Reading/Writing'),
    ))
    
    # Performance patterns
    best_study_time = models.CharField(max_length=20, blank=True, choices=(
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('evening', 'Evening'),
        ('night', 'Night'),
    ))
    
    average_focus_duration = models.IntegerField(default=25)  # in minutes
    retention_rate = models.FloatField(default=0.0)  # 0-1 scale
    
    # Generated insights
    strengths = models.JSONField(default=list, blank=True)
    improvement_areas = models.JSONField(default=list, blank=True)
    suggested_strategies = models.JSONField(default=list, blank=True)
    
    last_analyzed = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} Learning Pattern"