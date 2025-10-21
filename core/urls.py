from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('accounts/', include('accounts.urls')),
    path('courses/', include('courses.urls')),
    path('analytics/', include('analytics.urls')),
    path('ai/', include('ai_assistant.urls')),
    path('notes/', include('notes.urls')),
    path('collaboration/', include('collaboration.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)