from rest_framework import serializers
from .models import AccessLog


class AccessLogSerializer(serializers.ModelSerializer):
    """
    Serializer for the AccessLog model.
    The timestamp field is read-only.
    """
    class Meta:
        model = AccessLog
        fields = ['id', 'card_id', 'door_name', 'access_granted', 'timestamp', 'created_at']
        read_only_fields = ['id', 'timestamp', 'created_at']
    
    def validate_card_id(self, value):
        """
        card_id validation - cannot be empty and must be at least 2 characters long.
        """
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError(
                "card_id must be at least 2 characters long."
            )
        return value.strip()
    
    def validate_door_name(self, value):
        """
        door_name validation - cannot be empty.
        """
        if not value or len(value.strip()) < 1:
            raise serializers.ValidationError(
                "door_name cannot be empty."
            )
        return value.strip()
