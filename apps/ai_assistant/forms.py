from django import forms
from .models import AIConversation

class AIConversationForm(forms.ModelForm):
    class Meta:
        model = AIConversation
        fields = ['title', 'conversation_type', 'context_course', 'context_lesson', 'context_note']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'What would you like to discuss?',
                'class': 'w-full'
            }),
        }

class AIMessageForm(forms.Form):
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Ask me anything about your learning...',
            'class': 'w-full resize-none'
        })
    )
    
    include_context = forms.BooleanField(
        required=False,
        initial=True,
        label='Include my current learning context'
    )