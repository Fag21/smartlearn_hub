from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from courses.models import Enrollment, LessonProgress
from .models import UserLearningStat, StudySession, DailyGoal
from django.db.models import Sum 
@login_required
def dashboard(request):
    user = request.user
    user_stats, created = UserLearningStat.objects.get_or_create(user=user)
    
    # Get recent enrollments with progress
    enrollments = Enrollment.objects.filter(user=user).select_related('course')[:5]
    
    # Get today's goal
    today = timezone.now().date()
    daily_goal, created = DailyGoal.objects.get_or_create(user=user, date=today)
    
    # Get study sessions for the last 7 days
    seven_days_ago = timezone.now() - timedelta(days=7)
    recent_sessions = StudySession.objects.filter(
        user=user, 
        start_time__gte=seven_days_ago
    ).select_related('course')[:10]
    
    # Calculate weekly study time
    weekly_study_time = sum(session.duration for session in recent_sessions)
    
    # Get completion statistics
    total_lessons_completed = LessonProgress.objects.filter(
        user=user, 
        is_completed=True
    ).count()
    
    context = {
        'user_stats': user_stats,
        'enrollments': enrollments,
        'daily_goal': daily_goal,
        'recent_sessions': recent_sessions,
        'weekly_study_time': weekly_study_time,
        'total_lessons_completed': total_lessons_completed,
    }
    
    return render(request, 'analytics/dashboard.html', context)

@login_required
def progress_analytics(request):
    user = request.user
    
    # Get course progress data
    enrollments = Enrollment.objects.filter(user=user).select_related('course')
    
    # Get study time by day for the last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    daily_study_data = StudySession.objects.filter(
        user=user,
        start_time__gte=thirty_days_ago
    ).extra({
        'date': "DATE(start_time)"
    }).values('date').annotate(total_duration=models.Sum('duration'))
    
    context = {
        'enrollments': enrollments,
        'daily_study_data': list(daily_study_data),
    }
    
    return render(request, 'analytics/progress.html', context)