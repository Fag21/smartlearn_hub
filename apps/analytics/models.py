from django.db import models
from accounts.models import User
from courses.models import Course, Lesson

class UserLearningStat(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='learning_stats')
    total_study_time = models.IntegerField(default=0)  # in minutes
    average_session_time = models.IntegerField(default=0)
    days_streak = models.IntegerField(default=0)
    last_study_date = models.DateField(null=True, blank=True)
    goals_achieved = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username} Learning Stats"

class StudySession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_sessions')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='study_sessions')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(default=0)  # in minutes
    lessons_completed = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title} - {self.start_time.date()}"

class DailyGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_goals')
    date = models.DateField()
    target_minutes = models.IntegerField(default=30)
    actual_minutes = models.IntegerField(default=0)
    is_achieved = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['user', 'date']
    
    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.actual_minutes}/{self.target_minutes}min"