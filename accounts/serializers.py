from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import Profile, User


class ProfileSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField(read_only=True)
    daily_targets = serializers.SerializerMethodField()
    email = serializers.EmailField(read_only=True, source='user.email')

    class Meta:
        model = Profile
        fields = [
            'id', 'email', 'name', 'gender', 'weight', 'height',
            'birth_date', 'age', 'activity', 'goal', 'daily_targets', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'email', 'created_at', 'updated_at']

    def get_daily_targets(self, obj):
        return obj.calculate_daily_targets()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8,validators=[validate_password])

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
