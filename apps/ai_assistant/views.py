from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import openai
from django.conf import settings
from .models import AIConversation, AIMessage, AIRecommendation, LearningPattern
from .forms import AIConversationForm, AIMessageForm

@method_decorator(login_required, name='dispatch')
class ConversationListView(ListView):
    model = AIConversation
    template_name = 'ai_assistant/conversation_list.html'
    context_object_name = 'conversations'
    
    def get_queryset(self):
        return AIConversation.objects.filter(user=self.request.user, is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['conversation_form'] = AIConversationForm()
        return context

@method_decorator(login_required, name='dispatch')
class ConversationDetailView(DetailView):
    model = AIConversation
    template_name = 'ai_assistant/conversation_detail.html'
    context_object_name = 'conversation'
    
    def get_queryset(self):
        return AIConversation.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message_form'] = AIMessageForm()
        context['messages'] = self.object.messages.all()
        return context

@method_decorator(login_required, name='dispatch')
class ConversationCreateView(CreateView):
    model = AIConversation
    form_class = AIConversationForm
    template_name = 'ai_assistant/conversation_form.html'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        
        # Create welcome message
        welcome_message = AIMessage.objects.create(
            conversation=form.instance,
            message_type='assistant',
            content="Hello! I'm your AI learning assistant. How can I help you with your studies today?",
            tokens_used=0
        )
        
        messages.success(self.request, 'New conversation started!')
        return response
    
    def get_success_url(self):
        return reverse_lazy('ai_assistant:conversation_detail', kwargs={'pk': self.object.pk})

@login_required
def send_ai_message(request, pk):
    conversation = get_object_or_404(AIConversation, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = AIMessageForm(request.POST)
        if form.is_valid():
            user_message = form.cleaned_data['message']
            include_context = form.cleaned_data['include_context']
            
            # Save user message
            user_msg = AIMessage.objects.create(
                conversation=conversation,
                message_type='user',
                content=user_message
            )
            
            # Generate AI response (simulated for now)
            ai_response = generate_ai_response(conversation, user_message, include_context)
            
            # Save AI response
            ai_msg = AIMessage.objects.create(
                conversation=conversation,
                message_type='assistant',
                content=ai_response,
                tokens_used=len(ai_response.split())  # Rough estimate
            )
            
            # Update conversation timestamp
            conversation.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'user_message': user_message,
                    'ai_response': ai_response,
                    'timestamp': ai_msg.created_at.isoformat()
                })
            
            messages.success(request, 'Message sent!')
            return redirect('ai_assistant:conversation_detail', pk=pk)
    
    return redirect('ai_assistant:conversation_detail', pk=pk)

def generate_ai_response(conversation, user_message, include_context):
    """
    Generate AI response. This is a simplified version.
    In production, you would integrate with OpenAI API.
    """
    # Simple rule-based responses for demo
    user_message_lower = user_message.lower()
    
    if 'hello' in user_message_lower or 'hi' in user_message_lower:
        return "Hello! I'm your AI learning assistant. I can help you with:\n- Explaining concepts\n- Study recommendations\n- Quiz preparation\n- Career guidance\n\nWhat would you like to know?"
    
    elif 'explain' in user_message_lower:
        return "I'd be happy to explain that concept! Could you provide more details about what specific topic you'd like me to explain?"
    
    elif 'recommend' in user_message_lower:
        return "Based on your learning patterns, I recommend focusing on:\n1. Practice problems for better retention\n2. Breaking study sessions into 25-minute blocks\n3. Reviewing previous lessons before starting new ones\n\nWould you like specific course recommendations?"
    
    elif 'quiz' in user_message_lower or 'test' in user_message_lower:
        return "I can help you prepare for quizzes! I can:\n- Create practice questions\n- Explain difficult concepts\n- Suggest review strategies\n\nWhat subject is your quiz about?"
    
    else:
        return "Thank you for your message! As an AI learning assistant, I'm here to help you with:\n\n📚 **Course Content** - Explanations and examples\n🎯 **Study Strategies** - Personalized learning techniques\n📊 **Progress Analysis** - Insights from your learning data\n💡 **Career Guidance** - Skills and learning paths\n\nHow can I assist you with your learning goals today?"

@login_required
def get_recommendations(request):
    user_recommendations = AIRecommendation.objects.filter(
        user=request.user,
        is_accepted=False
    )[:10]
    
    # Get learning pattern
    learning_pattern, created = LearningPattern.objects.get_or_create(user=request.user)
    
    context = {
        'recommendations': user_recommendations,
        'learning_pattern': learning_pattern,
    }
    
    return render(request, 'ai_assistant/recommendations.html', context)

@login_required
@csrf_exempt
def accept_recommendation(request, pk):
    if request.method == 'POST':
        recommendation = get_object_or_404(AIRecommendation, pk=pk, user=request.user)
        recommendation.is_accepted = True
        recommendation.save()
        
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def learning_insights(request):
    learning_pattern, created = LearningPattern.objects.get_or_create(user=request.user)
    
    # Get some basic analytics (in a real app, this would be more sophisticated)
    from courses.models import Enrollment, LessonProgress
    from notes.models import Note
    
    total_courses = Enrollment.objects.filter(user=request.user).count()
    completed_lessons = LessonProgress.objects.filter(user=request.user, is_completed=True).count()
    total_notes = Note.objects.filter(user=request.user).count()
    
    context = {
        'learning_pattern': learning_pattern,
        'total_courses': total_courses,
        'completed_lessons': completed_lessons,
        'total_notes': total_notes,
    }
    
    return render(request, 'ai_assistant/learning_insights.html', context)