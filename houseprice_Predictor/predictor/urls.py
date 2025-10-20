from django.urls import path
from .views import PredictPrice
from .views import home, PredictPrice
urlpatterns = [
    path('predict/', PredictPrice.as_view(), name='predict_price'),
]

from .views import home, PredictPrice

urlpatterns = [
    path("", home, name="home"),
    path("predict/", PredictPrice.as_view(), name="predict_price"),
]