from django.shortcuts import render


def index(request):
    return render(request, 'index.html')

def tos(request):
    return render(request, 'tos.html')

def privacy_policy(request):
    return render(request, 'privacy_policy.html')