from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import HouseDataSerializer
import joblib
import numpy as np
import os
from django.conf import settings

# === مسیر اصلی پروژه ===
BASE_DIR = settings.BASE_DIR

# === مسیر فایل‌های مدل، اسکیلر و انکودر ===
MODEL_PATH = os.path.join(BASE_DIR, "house_price_xgb_final.joblib")
SCALER_PATH = os.path.join(BASE_DIR, "scaler.joblib")
ENCODER_PATH = os.path.join(BASE_DIR, "address_encoder.joblib")

# === لود مدل‌ها فقط یک‌بار در زمان شروع سرور ===
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

try:
    encoder = joblib.load(ENCODER_PATH)
except Exception as e:
    encoder = None
    _encoder_load_error = str(e)

# === API اصلی پیش‌بینی قیمت ===
class PredictPrice(APIView):
    def post(self, request):
        # اعتبارسنجی ورودی‌ها
        serializer = HouseDataSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # بررسی لود بودن فایل‌ها
        if model is None or scaler is None or encoder is None:
            err = {}
            if model is None:
                err['model'] = f"Model not loaded: {_model_load_error}"
            if scaler is None:
                err['scaler'] = f"Scaler not loaded: {_scaler_load_error}"
            if encoder is None:
                err['encoder'] = f"Encoder not loaded: {_encoder_load_error}"
            return Response({"error": "Model/scaler/encoder missing", "details": err},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        data = serializer.validated_data

        # === تبدیل آدرس از متن به مقدار عددی ===
        try:
            address_encoded = int(encoder.transform([data["Address"]])[0])
        except Exception:
            return Response(
                {"error": f"آدرس '{data['Address']}' معتبر نیست یا در مدل وجود ندارد."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # === ساخت آرایه ویژگی‌ها (features) ===
        try:
            features = np.array([[
                data["Priceـperـsquareـmeter"],
                data["Area"],
                data["Warehouse"],
                data["Elevator"],
                data["Parking"],
                data["Room"],
                address_encoded
            ]], dtype=float)
        except KeyError as e:
            return Response({"error": f"Feature missing: {str(e)}"}, status=400)

        # === نرمال‌سازی و پیش‌بینی ===
        try:
            scaled = scaler.transform(features)
            pred = model.predict(scaled)[0]
        except Exception as e:
            return Response({"error": f"Prediction failed: {str(e)}"}, status=500)

        # === فرمت خروجی ===
        formatted_price = f"{int(pred):,} تومان"
        response_data = {"status": "success","input_data": data,"prediction": {
                "price_toman": formatted_price,
                "raw_value": float(pred)
            }
        }
        return Response(response_data, status=status.HTTP_200_OK)
from django.shortcuts import render

def home(request):
    return render(request, "predictor/predict.html")
