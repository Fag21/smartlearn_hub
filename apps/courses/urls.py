from django.urls import path
from . import views
app_name='courses'
urlpatterns = [
    path('', views.CourseListView.as_view(), name='course_list'),
    path('category/<str:category>/', views.CourseListView.as_view(), name='course_list_by_category'),
    path('<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('<int:pk>/enroll/', views.CourseEnrollView.as_view(), name='course_enroll'),
    path('<int:pk>/learn/', views.course_learn, name='course_learn'),
    path('<int:course_pk>/lesson/<int:lesson_pk>/', views.lesson_detail, name='lesson_detail'),
    path('my-courses/', views.UserCoursesListView.as_view(), name='my_courses'),
]