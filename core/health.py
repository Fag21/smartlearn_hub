import json
from django.http import JsonResponse
from django.views import View
from django.db import connections
from django.core.cache import cache
from django.conf import settings


class HealthCheckView(View):
    def get(self, request):
        checks = {}
        status = 200
        
        # Database check
        try:
            db_conn = connections['default']
            db_conn.ensure_connection()
            checks['database'] = 'healthy'
        except Exception as e:
            checks['database'] = f'unhealthy: {str(e)}'
            status = 503
        
        # Redis/Cache check
        try:
            cache.set('health_check', 'ok', 10)
            if cache.get('health_check') == 'ok':
                checks['cache'] = 'healthy'
            else:
                checks['cache'] = 'unhealthy: cache not working'
                status = 503
        except Exception as e:
            checks['cache'] = f'unhealthy: {str(e)}'
            status = 503
        
        # Celery check (optional)
        try:
            from celery import current_app
            inspect = current_app.control.inspect()
            if inspect.ping():
                checks['celery'] = 'healthy'
            else:
                checks['celery'] = 'unhealthy: no workers responding'
                status = 503
        except Exception as e:
            checks['celery'] = f'unhealthy: {str(e)}'
            status = 503
        
        # OpenAI check (optional - just check if key is configured)
        if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != 'your-openai-api-key':
            checks['openai'] = 'configured'
        else:
            checks['openai'] = 'not configured'
        
        response_data = {
            'status': 'healthy' if status == 200 else 'unhealthy',
            'checks': checks,
        }
        
        return JsonResponse(response_data, status=status)


def health_check(request):
    """Simple health check for load balancers"""
    return JsonResponse({'status': 'ok'})