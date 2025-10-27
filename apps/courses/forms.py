from django import forms
from .models import Course, Module, Lesson, Category

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'short_description', 'categories', 
                 'level', 'duration', 'price', 'thumbnail']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'short_description': forms.Textarea(attrs={'rows': 2}),
        }

class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'description', 'order', 'duration']

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'content', 'video_url', 'lesson_type', 'duration', 'order', 'is_free']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 6}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'color', 'icon']