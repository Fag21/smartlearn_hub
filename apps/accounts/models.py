from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('instructor', 'Instructor'),
        ('admin', 'Administrator'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='student')
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    email_verified = models.BooleanField(default=False)
    email_notifications = models.BooleanField(default=True)
    
    # Learning preferences
    learning_goals = models.TextField(blank=True)
    current_level = models.CharField(max_length=100, blank=True)
    preferred_language = models.CharField(max_length=10, default='en')
    time_zone = models.CharField(max_length=50, default='UTC')
    
    # Social fields
    twitter = models.CharField(max_length=100, blank=True)
    linkedin = models.CharField(max_length=100, blank=True)
    github = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username
    
    def get_absolute_url(self):
        return reverse('accounts:profile', kwargs={'username': self.username})
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    points = models.IntegerField(default=0)
    streak = models.IntegerField(default=0)
    daily_goal = models.IntegerField(default=30)  # minutes
    total_study_time = models.IntegerField(default=0)  # minutes
    completed_courses = models.IntegerField(default=0)
    achievements_unlocked = models.IntegerField(default=0)
    
    # Learning statistics
    average_score = models.FloatField(default=0.0)
    quizzes_taken = models.IntegerField(default=0)
    notes_created = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def update_streak(self):
        # This would be updated by a daily task
        pass
    
    def add_points(self, points):
        self.points += points
        self.save()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()