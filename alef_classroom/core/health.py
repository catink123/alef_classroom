"""
Health check utilities for the application.
"""

import os
import psutil
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """
    Health check endpoint for monitoring.
    Returns 200 if the application is healthy, 503 otherwise.
    """
    health_data = {
        'status': 'healthy',
        'checks': {}
    }
    
    # Check disk usage
    disk_usage = psutil.disk_usage('/')
    disk_percent = (disk_usage.used / disk_usage.total) * 100
    health_data['checks']['disk_usage'] = {
        'status': 'ok' if disk_percent < 90 else 'warning',
        'percent_used': round(disk_percent, 2)
    }
    
    # Check memory usage
    memory = psutil.virtual_memory()
    memory_mb = memory.available / (1024 * 1024)
    health_data['checks']['memory'] = {
        'status': 'ok' if memory_mb > 100 else 'warning',
        'available_mb': round(memory_mb, 2)
    }
    
    # Check database connection
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_data['checks']['database'] = {'status': 'ok'}
    except Exception as e:
        health_data['checks']['database'] = {
            'status': 'error',
            'error': str(e)
        }
        health_data['status'] = 'unhealthy'
    
    # Check Redis connection
    try:
        import redis
        r = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://redis:6379/0'))
        r.ping()
        health_data['checks']['redis'] = {'status': 'ok'}
    except Exception as e:
        health_data['checks']['redis'] = {
            'status': 'error',
            'error': str(e)
        }
        health_data['status'] = 'unhealthy'
    
    # Determine overall status
    if any(check.get('status') == 'error' for check in health_data['checks'].values()):
        health_data['status'] = 'unhealthy'
    elif any(check.get('status') == 'warning' for check in health_data['checks'].values()):
        health_data['status'] = 'degraded'
    
    status_code = 200 if health_data['status'] == 'healthy' else 503
    return JsonResponse(health_data, status=status_code)
