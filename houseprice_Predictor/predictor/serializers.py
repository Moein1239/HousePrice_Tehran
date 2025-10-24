from rest_framework import serializers

class HouseDataSerializer(serializers.Serializer):
    Priceـperـsquareـmeter  = serializers.FloatField()
    Area = serializers.FloatField()
    Warehouse=serializers.FloatField()
    Elevator=serializers.FloatField()
    Parking = serializers.FloatField()
    Room = serializers.FloatField()
    Address= serializers.CharField()
