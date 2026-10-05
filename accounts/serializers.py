from rest_framework import serializers
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField(read_only=True)
    daily_targets = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            'id', 'name', 'gender', 'weight', 'height',
            'birth_date', 'age', 'activity', 'goal', 'daily_targets', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_daily_targets(self, obj):
        return obj.calculate_daily_targets()
