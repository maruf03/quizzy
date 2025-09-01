from django.shortcuts import render
from django.http import JsonResponse
from django.db import connections
import time

APP_START_TIME = time.time()

def health(request):  # Liveness & basic readiness
	status = 200
	db_ok = True
	try:
		connections['default'].cursor()
	except Exception:
		db_ok = False
		status = 503
	data = {
		'status': 'ok' if status==200 else 'degraded',
		'uptime_seconds': int(time.time() - APP_START_TIME),
		'db': db_ok,
	}
	return JsonResponse(data, status=status)


def error_400(request, exception):  # pragma: no cover
	return render(request, '400.html', status=400)

def error_403(request, exception):  # pragma: no cover
	return render(request, '403.html', status=403)

def error_404(request, exception):  # pragma: no cover
	return render(request, '404.html', status=404)

def error_500(request):  # pragma: no cover
	return render(request, '500.html', status=500)

