from django.urls import path
from .views import PredictPriceAPI, predict_price

urlpatterns = [
    path('', predict_price, name='predict_price'),            # صفحه HTML  /api/
    path('predict/', PredictPriceAPI.as_view(), name='api_predict'),  # API  /api/predict/
]


from django.shortcuts import render

def home(request):
    return render(request, 'home.html')
