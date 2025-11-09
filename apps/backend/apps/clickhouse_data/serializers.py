from rest_framework import serializers
from .models import OptionData, OHLCData, NewsData

class OptionDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptionData
        fields = '__all__'

class OHLCDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = OHLCData
        fields = '__all__'

class NewsDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsData
        fields = '__all__'
