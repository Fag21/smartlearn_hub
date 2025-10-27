from django.contrib import admin
from .models import Category, Course, Module, Lesson, Enrollment, LessonProgress

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1

class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'icon']
    search_fields = ['name']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'level', 'price', 'is_published', 'created_at']
    list_filter = ['level', 'is_published', 'created_at']
    search_fields = ['title', 'description']
    inlines = [ModuleInline]

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    list_filter = ['course']
    inlines = [LessonInline]

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'lesson_type', 'duration', 'order']
    list_filter = ['lesson_type', 'module__course']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'enrolled_at', 'progress', 'is_completed']
    list_filter = ['is_completed', 'enrolled_at']

@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'is_completed', 'last_accessed']
    list_filter = ['is_completed']