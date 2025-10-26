from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
import joblib
import numpy as np
import pandas as pd
import os
from django.conf import settings

# ----------------- Load Models -----------------
BASE_DIR = settings.BASE_DIR  
MODEL_PATH = os.path.join(BASE_DIR, "house_price_xgb_final.joblib")
SCALER_PATH = os.path.join(BASE_DIR, "scaler.joblib")
ENCODER_PATH = os.path.join(BASE_DIR, "address_encoder.joblib")

xgb_model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
address_encoder = joblib.load(ENCODER_PATH)

most_common_address_encoded = 0  # default
try:
    classes = list(address_encoder.classes_)
except Exception:
    classes = []

# ----------------- Serializer -----------------
class HouseDataSerializer(serializers.Serializer):
    Area = serializers.FloatField()
    Room = serializers.IntegerField()
    Parking = serializers.IntegerField()
    Warehouse = serializers.IntegerField()
    Elevator = serializers.IntegerField()
    Address = serializers.CharField()
    Priceـperـsquareـmeter = serializers.FloatField()

# ----------------- API View -----------------
class PredictPriceAPI(APIView):
    def post(self, request):
        serializer = HouseDataSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            # Encode address
            address_text = str(data['Address'])
            if address_text in list(address_encoder.classes_):
                address_num = int(address_encoder.transform([address_text])[0])
            else:
                address_num = int(most_common_address_encoded)

            # Prepare input
            X = pd.DataFrame([[data['Priceـperـsquareـmeter'],
                                data['Area'], 
                                int(data['Warehouse']),
                                 int(data['Elevator']),
                                 int(data['Parking']),
                                 int(data['Room']),
                                 address_num
                                 ]],
                             columns=['Priceـperـsquareـmeter','Area','Warehouse','Elevator','Parking','Room','Address'])

            x_scaled = scaler.transform(X)
            pred = xgb_model.predict(x_scaled)[0]
            pred = max(pred, 0)
            formatted = f"{int(round(pred)):,}"
            return Response({"status": "success",
                             "input_data": {  "Priceـperـsquareـmeter": data['Priceـperـsquareـmeter'],
                                            "Area": data['Area'],"Warehouse": data['Warehouse'],
                                            "Elevator": data['Elevator'],
                                            "Parking": data['Parking'],
                                            "Room": data['Room'],
                                            "Address": data['Address']},
                             "prediction": {"price_toman": f"{formatted} تومان","raw_value": pred}}, status=status.HTTP_200_OK)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ----------------- HTML Form View -----------------
def predict_price(request):
    prediction = None
    error = None
    negative_input_warning = None  
        
    if request.method == "POST":
        try:
            Priceـperـsquareـmeter = float(request.POST.get('Priceـperـsquareـmeter', 0))
            area = float(request.POST.get('area', 0))
            warehouse = int(request.POST.get('warehouse', 0))
            elevator = int(request.POST.get('elevator', 0))
            parking = int(request.POST.get('parking', 0))
            rooms = int(request.POST.get('rooms', 0))
            address = request.POST.get('address', '')



            if address in list(address_encoder.classes_):
                address_num = int(address_encoder.transform([address])[0])
            else:
                address_num = int(most_common_address_encoded)

            X = pd.DataFrame([[Priceـperـsquareـmeter,area, warehouse ,elevator,parking,rooms, address_num, ]],
                             columns=['Priceـperـsquareـmeter','Area','Warehouse','Elevator','Parking','Room','Address',])
            x_scaled = scaler.transform(X)
            pred = xgb_model.predict(x_scaled)[0]

            if pred < 0:
                prediction = None
                negative_input_warning = "The inputs are unrealistic, the prediction was negative. Please adjust the inputs."
            else:
                prediction = f"{int(round(pred)):,}"
        except Exception as e:
            error = str(e)

    address_choices = list(address_encoder.classes_)
    
    
    return render(request, "predictor/predict.html", {
        "prediction": prediction,
        "error": error,
        "negative_input_warning": negative_input_warning,
        "address_choices": address_choices
    })

from django.shortcuts import render

def home(request):
    return render(request, 'predictor/home.html')
