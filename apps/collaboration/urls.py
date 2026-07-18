from django.urls import path
from . import views

app_name = 'collaboration'
urlpatterns = [
    # Study Groups
    path('groups/', views.StudyGroupListView.as_view(), name='study_groups'), # type: ignore
    path('groups/create/', views.StudyGroupCreateView.as_view(), name='study_group_create'),
    path('groups/<int:pk>/', views.StudyGroupDetailView.as_view(), name='study_group_detail'),
    path('groups/<int:pk>/join/', views.join_study_group, name='join_study_group'),
    path('groups/<int:pk>/leave/', views.leave_study_group, name='leave_study_group'),
    
    # Chat
    path('groups/<int:pk>/chat/',views.send_chat_message, name='send_chat_message'),
    
    # Resources
    path('groups/<int:pk>/resources/', views.group_resources, name='group_resources'),
    path('groups/<int:pk>/resources/upload/', views.upload_resource, name='upload_resource'),
    
    # Assignments
    path('groups/<int:pk>/assignments/', views.group_assignments, name='group_assignments'),
    path('groups/<int:pk>/assignments/create/', views.create_assignment, name='create_assignment'),
]