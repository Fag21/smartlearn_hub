from django import forms
from .models import Note, NoteCategory, NoteTag

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'content', 'category', 'note_type', 'visibility', 'is_pinned']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 15,
                'class': 'markdown-editor',
                'placeholder': 'Write your note in Markdown...'
            }),
            'title': forms.TextInput(attrs={
                'placeholder': 'Note title...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Only show categories belonging to the current user
            self.fields['category'].queryset = NoteCategory.objects.filter(user=user)

class NoteCategoryForm(forms.ModelForm):
    class Meta:
        model = NoteCategory
        fields = ['name', 'color', 'icon']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
        }

class NoteTagForm(forms.ModelForm):
    class Meta:
        model = NoteTag
        fields = ['name', 'color']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
        }

class QuickNoteForm(forms.ModelForm):
    """Form for creating quick notes without all fields"""
    class Meta:
        model = Note
        fields = ['title', 'content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Start typing your note...'
            }),
            'title': forms.TextInput(attrs={
                'placeholder': 'Quick note title...'
            }),
        }