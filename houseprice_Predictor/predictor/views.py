from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import HouseDataSerializer
import joblib
import numpy as np
import os
from django.conf import settings



# یکبار مدل و اسکِیلر را لود کن (با مسیر نسبی به BASE_DIR)
BASE_DIR = settings.BASE_DIR  # از تنظیمات Django
MODEL_PATH = os.path.join(BASE_DIR, "house_price_xgb_final.joblib")
SCALER_PATH = os.path.join(BASE_DIR, "scaler.joblib")

# اگر فایل‌ها در مسیر دیگری قرار دادی، مسیر بالا را ویرایش کن.

try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    model = None
    _model_load_error = str(e)

try:
    scaler = joblib.load(SCALER_PATH)
except Exception as e:
    scaler = None
    _scaler_load_error = str(e)

class PredictPrice(APIView):
    def post(self, request):
        serializer = HouseDataSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if model is None or scaler is None:
            err = {}
            if model is None:
                err['model'] = f"Model not loaded: {_model_load_error}"
            if scaler is None:
                err['scaler'] = f"Scaler not loaded: {_scaler_load_error}"
            return Response({"error": "Model/scaler missing", "details": err}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        data = serializer.validated_data
        
        features = np.array([[
            data["Priceـperـsquareـmeter"],
            data["Area"],
            data["Parking"],
            data["Room"],
            data["Address"],
            data["Warehouse"],
            data["Elevator"]
        ]], dtype=float)

        # scale و predict
        scaled = scaler.transform(features)
        pred = model.predict(scaled)[0]
        # معمولاً Price بر حسب تومان است؛ در صورت نیاز رُند کن
        formatted_price = f"{int(pred):,} تومان"
        return Response({"predicted_price": formatted_price})

# Create your views here.
