from django.urls import path
from . import views

# Remove app_name temporarily to test
app_name = 'notes'

urlpatterns = [
    path('', views.NoteListView.as_view(), name='note_list'),
    path('create/', views.NoteCreateView.as_view(), name='note_create'),
    path('quick-create/', views.quick_create_note, name='quick_create'),
    path('<int:pk>/', views.NoteDetailView.as_view(), name='note_detail'),
    path('<int:pk>/edit/', views.NoteUpdateView.as_view(), name='note_edit'),
    path('<int:pk>/delete/', views.NoteDeleteView.as_view(), name='note_delete'),
    path('<int:pk>/pin/', views.toggle_pin_note, name='toggle_pin'),
    path('<int:pk>/archive/', views.archive_note, name='archive_note'),
    path('<int:pk>/ai-summary/', views.generate_ai_summary, name='ai_summary'),
    path('statistics/', views.note_statistics, name='statistics'),
]