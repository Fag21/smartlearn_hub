from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.db.models import Q, Count
from django.http import JsonResponse
from .models import Note, NoteCategory, NoteTag, NoteVersion, NoteCollaborator
from .forms import NoteForm, NoteCategoryForm, QuickNoteForm
import json

@method_decorator(login_required, name='dispatch')
class NoteListView(ListView):
    model = Note
    template_name = 'notes/note_list.html'
    context_object_name = 'notes'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Note.objects.filter(user=self.request.user, is_archived=False)
        
        # Filter by category
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Filter by tag
        tag_id = self.request.GET.get('tag')
        if tag_id:
            queryset = queryset.filter(tags__id=tag_id)
        
        # Filter by type
        note_type = self.request.GET.get('type')
        if note_type:
            queryset = queryset.filter(note_type=note_type)
        
        # Search
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(summary__icontains=search_query)
            )
        
        # Show pinned notes first
        return queryset.order_by('-is_pinned', '-updated_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = NoteCategory.objects.filter(user=self.request.user)
        context['tags'] = NoteTag.objects.filter(user=self.request.user)
        context['quick_note_form'] = QuickNoteForm()
        return context

@method_decorator(login_required, name='dispatch')
class NoteDetailView(DetailView):
    model = Note
    template_name = 'notes/note_detail.html'
    context_object_name = 'note'
    
    def get_queryset(self):
        # Users can view their own notes and shared notes
        return Note.objects.filter(
            Q(user=self.request.user) | 
            Q(collaborators__user=self.request.user) |
            Q(visibility='public')
        ).distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_owner'] = self.object.user == self.request.user
        context['can_edit'] = (context['is_owner'] or 
                             self.object.collaborators.filter(
                                 user=self.request.user, can_edit=True
                             ).exists())
        return context

@method_decorator(login_required, name='dispatch')
class NoteCreateView(CreateView):
    model = Note
    form_class = NoteForm
    template_name = 'notes/note_form.html'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Note created successfully!')
        return response
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = Note(user=self.request.user)
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = NoteCategory.objects.filter(user=self.request.user)
        return context

@method_decorator(login_required, name='dispatch')
class NoteUpdateView(UpdateView):
    model = Note
    form_class = NoteForm
    template_name = 'notes/note_form.html'
    
    def get_queryset(self):
        # Users can edit their own notes and notes they have edit access to
        return Note.objects.filter(
            Q(user=self.request.user) | 
            Q(collaborators__user=self.request.user, collaborators__can_edit=True)
        ).distinct()
    
    def form_valid(self, form):
        # Create version before saving
        note = form.save(commit=False)
        current_version = note.versions.count() + 1
        NoteVersion.objects.create(
            note=note,
            content=note.content,
            version_number=current_version,
            user=self.request.user
        )
        response = super().form_valid(form)
        messages.success(self.request, 'Note updated successfully!')
        return response

@method_decorator(login_required, name='dispatch')
class NoteDeleteView(DeleteView):
    model = Note
    template_name = 'notes/note_confirm_delete.html'
    success_url = reverse_lazy('notes:note_list')
    
    def get_queryset(self):
        return Note.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Note deleted successfully!')
        return super().delete(request, *args, **kwargs)

@login_required
def quick_create_note(request):
    if request.method == 'POST':
        form = QuickNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()
            messages.success(request, 'Quick note created!')
            return redirect('notes:note_list')
    
    return redirect('notes:note_list')

@login_required
def toggle_pin_note(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    note.is_pinned = not note.is_pinned
    note.save()
    
    action = "pinned" if note.is_pinned else "unpinned"
    messages.success(request, f'Note {action}!')
    
    return redirect('notes:note_list')

@login_required
def archive_note(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    note.is_archived = True
    note.save()
    messages.success(request, 'Note archived!')
    return redirect('notes:note_list')

@login_required
def generate_ai_summary(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    
    # This would integrate with OpenAI API
    # For now, we'll create a simple summary
    if note.content:
        # Simple summary - first 100 chars
        note.summary = note.content[:100] + '...' if len(note.content) > 100 else note.content
        note.ai_summary_generated = True
        note.save()
        messages.success(request, 'AI summary generated!')
    else:
        messages.error(request, 'Note has no content to summarize.')
    
    return redirect('notes:note_detail', pk=pk)

@login_required
def note_statistics(request):
    user_notes = Note.objects.filter(user=request.user)
    
    stats = {
        'total_notes': user_notes.count(),
        'pinned_notes': user_notes.filter(is_pinned=True).count(),
        'archived_notes': user_notes.filter(is_archived=True).count(),
        'total_words': sum(note.word_count for note in user_notes),
        'total_reading_time': sum(note.reading_time for note in user_notes),
    }
    
    # Notes by type
    notes_by_type = user_notes.values('note_type').annotate(count=Count('id'))
    
    # Recent activity
    recent_notes = user_notes.order_by('-updated_at')[:5]
    
    context = {
        'stats': stats,
        'notes_by_type': notes_by_type,
        'recent_notes': recent_notes,
    }
    
    return render(request, 'notes/note_statistics.html', context)