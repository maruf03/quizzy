from django.shortcuts import render

def error_400(request, exception):  # pragma: no cover
	return render(request, '400.html', status=400)

def error_403(request, exception):  # pragma: no cover
	return render(request, '403.html', status=403)

def error_404(request, exception):  # pragma: no cover
	return render(request, '404.html', status=404)

def error_500(request):  # pragma: no cover
	return render(request, '500.html', status=500)
