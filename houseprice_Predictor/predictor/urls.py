from django.urls import path
from .views import PredictPrice

urlpatterns = [
    path('predict/', PredictPrice.as_view(), name='predict_price'),
]

