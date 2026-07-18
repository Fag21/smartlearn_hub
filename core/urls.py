from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from .health import health_check, HealthCheckView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('health/', health_check, name='health_check'),
    path('health/detail/', HealthCheckView.as_view(), name='health_check_detail'),
    path('notes/', include('notes.urls')),
    # Apps with namespaces
    path('accounts/', include('accounts.urls',)),
    path('courses/', include('courses.urls')),
    path('analytics/', include(('analytics.urls', 'analytics'), namespace='analytics')),
    path('collaboration/', include(('collaboration.urls', 'collaboration'), namespace='collaboration')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)