from rest_framework import serializers

class BaseSerializerMixin:
    """공통 serializer mixin"""
    def to_representation(self, instance):
        # 날짜 포맷 일관성
        rep = super().to_representation(instance)
        for key in ['created_at', 'updated_at', 'timestamp', 'published_at']:
            if key in rep and rep[key]:
                rep[key] = rep[key][:19].replace("T", " ")  # ISO → "YYYY-MM-DD HH:MM:SS"
        return rep
