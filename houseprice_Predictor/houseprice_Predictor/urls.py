
from django.contrib import admin
from django.urls import path, include
from predictor import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('predictor.urls')),  # API root: /api/predict/
    path('', views.home, name='home'),
]
