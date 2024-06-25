from django.http import HttpResponse
from django.shortcuts import render
from cafejari.settings import env


def index(request):
    return render(request, 'index.html')

def tos(request):
    return render(request, 'tos.html')

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

app_ads_txt_id = env('APP_ADS_TXT_ID')
app_ads_txt_code = env('APP_ADS_TXT_CODE')

def app_ads(request):
    return HttpResponse(f"google.com, {app_ads_txt_id}, DIRECT, {app_ads_txt_code}")
