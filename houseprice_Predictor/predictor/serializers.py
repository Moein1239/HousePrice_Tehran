from rest_framework import serializers

class HouseDataSerializer(serializers.Serializer):
    Priceـperـsquareـmeter = serializers.FloatField()
    Area = serializers.FloatField()
    Avg_Price_By_address = serializers.FloatField()
    Room = serializers.FloatField()
    Address=serializers.FloatField()