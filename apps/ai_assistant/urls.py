from django.urls import path
from . import views

app_name = 'ai_assistant'

urlpatterns = [
    path('', views.ConversationListView.as_view(), name='conversation_list'),
    path('conversations/create/', views.ConversationCreateView.as_view(), name='conversation_create'),
    path('conversations/<int:pk>/', views.ConversationDetailView.as_view(), name='conversation_detail'),
    path('conversations/<int:pk>/send/', views.send_ai_message, name='send_message'),
    path('recommendations/', views.get_recommendations, name='recommendations'),
    path('recommendations/<int:pk>/accept/', views.accept_recommendation, name='accept_recommendation'),
    path('insights/', views.learning_insights, name='learning_insights'),
]