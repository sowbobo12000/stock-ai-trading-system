from rest_framework import serializers
from .models import GammaExposure, SignalScore
from core.serializers import BaseSerializerMixin
from core.choices import DealerPosition, SignalTypeChoices

# ✅ GammaExposure
class GammaExposureSerializer(BaseSerializerMixin, serializers.ModelSerializer):
    dealer_position = serializers.ChoiceField(choices=DealerPosition.choices)

    class Meta:
        model = GammaExposure
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


# ✅ SignalScore
class SignalScoreSerializer(BaseSerializerMixin, serializers.ModelSerializer):
    signal_type = serializers.ChoiceField(choices=SignalTypeChoices.choices)
    score = serializers.FloatField(min_value=0.0, max_value=100.0)

    class Meta:
        model = SignalScore
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
