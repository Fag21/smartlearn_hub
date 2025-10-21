from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True)
    learning_goals = models.TextField(blank=True)
    current_level = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return self.username
 
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    streak = models.IntegerField(default=0)
    time_zone = models.CharField(max_length=50, default='UTC')
    
    def __str__(self):
        return f"{self.user.username}'s Profile"