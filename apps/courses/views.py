from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.db.models import Q, Count, Avg
from .models import Course, Module, Lesson, Enrollment, LessonProgress, Category
from .forms import CourseForm, ModuleForm, LessonForm

class CourseListView(ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Course.objects.filter(is_published=True).annotate(
            avg_rating=Avg('rating'),
            student_count=Count('students')
        )
        
        # Filter by category
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(categories__name=category_slug)
        
        # Filter by level
        level = self.request.GET.get('level')
        if level:
            queryset = queryset.filter(level=level)
        
        # Search
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(short_description__icontains=search_query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['levels'] = Course.LEVEL_CHOICES
        return context

class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        
        # Check if user is enrolled
        if self.request.user.is_authenticated:
            context['is_enrolled'] = Enrollment.objects.filter(
                user=self.request.user, course=course
            ).exists()
        else:
            context['is_enrolled'] = False
        
        # Get course modules with lessons
        context['modules'] = course.modules.prefetch_related('lessons').all()
        
        # Get similar courses
        context['similar_courses'] = Course.objects.filter(
            categories__in=course.categories.all()
        ).exclude(id=course.id).distinct()[:4]
        
        return context

@method_decorator(login_required, name='dispatch')
class CourseEnrollView(DetailView):
    model = Course
    template_name = 'courses/course_enroll.html'
    
    def get(self, request, *args, **kwargs):
        course = self.get_object()
        
        # Check if already enrolled
        enrollment, created = Enrollment.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={'progress': 0.0}
        )
        
        if created:
            course.students.add(request.user)
            course.enrollment_count += 1
            course.save()
            messages.success(request, f'Successfully enrolled in {course.title}!')
        else:
            messages.info(request, f'You are already enrolled in {course.title}')
        
        return redirect('courses:course_detail', pk=course.pk)

@login_required
def course_learn(request, pk):
    course = get_object_or_404(Course, pk=pk)
    
    # Check if user is enrolled
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
    
    # Get modules with lessons
    modules = course.modules.prefetch_related('lessons').all()
    
    # Get user's lesson progress
    lesson_progress = {
        progress.lesson_id: progress 
        for progress in LessonProgress.objects.filter(
            user=request.user, 
            lesson__module__course=course
        )
    }
    
    context = {
        'course': course,
        'modules': modules,
        'enrollment': enrollment,
        'lesson_progress': lesson_progress,
    }
    
    return render(request, 'courses/course_learn.html', context)

@login_required
def lesson_detail(request, course_pk, lesson_pk):
    course = get_object_or_404(Course, pk=course_pk)
    lesson = get_object_or_404(Lesson, pk=lesson_pk, module__course=course)
    
    # Check if user is enrolled
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
    
    # Get or create lesson progress
    lesson_progress, created = LessonProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson
    )
    
    # Get next and previous lessons
    lessons = list(Lesson.objects.filter(module__course=course).order_by('module__order', 'order'))
    current_index = lessons.index(lesson)
    
    next_lesson = lessons[current_index + 1] if current_index < len(lessons) - 1 else None
    prev_lesson = lessons[current_index - 1] if current_index > 0 else None
    
    if request.method == 'POST' and 'complete' in request.POST:
        lesson_progress.is_completed = True
        lesson_progress.save()
        messages.success(request, 'Lesson marked as completed!')
        return redirect('courses:lesson_detail', course_pk=course_pk, lesson_pk=lesson_pk)
    
    context = {
        'course': course,
        'lesson': lesson,
        'enrollment': enrollment,
        'lesson_progress': lesson_progress,
        'next_lesson': next_lesson,
        'prev_lesson': prev_lesson,
    }
    
    return render(request, 'courses/lesson_detail.html', context)

@method_decorator(login_required, name='dispatch')
class UserCoursesListView(ListView):
    model = Enrollment
    template_name = 'courses/my_courses.html'
    context_object_name = 'enrollments'
    
    def get_queryset(self):
        return Enrollment.objects.filter(user=self.request.user).select_related('course')