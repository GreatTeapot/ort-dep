import re

from rest_framework import serializers

from .models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    location_country = serializers.CharField(source='get_location_country_display', allow_blank=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'avatar', 'first_name', 'last_name','age', 'school','location_country', 'about_you')


class UserRegisSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    # confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'password',  'first_name', 'last_name', 'school', 'age', 'location_country', 'about_you')
        extra_kwargs = {
            'username': {'write_only': True},
            'email': {'write_only': True},
            'password': {'write_only': True},
            'first_name': {'required': False,'write_only': True},
            'last_name': {'required': False,'write_only': True},
            'age': {'required': False, 'write_only': True},
            'school': {'required': False, 'write_only': True},
            'location_country': {'required': False, 'write_only': True},
            'about_you': {'required': False, 'write_only': True},

        }

    def validate_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("Password must be at least 6 characters long.")

        if not re.match("^[a-zA-Z0-9]+$", value):
            raise serializers.ValidationError("Password must contain only letters and digits.")

        return value

    def validate_username(self, value):
        if not re.match("^[a-zA-Z0-9_-]+$", value):
            raise serializers.ValidationError("Username can only contain letters, digits, '_', '-', '?'.")

        return value

    def validate_age(self, value):
        if value is not None and (value < 0 or value > 100):
            raise serializers.ValidationError("Age must be between 0 and 100.")

        return value

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data.get('email', ''),
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            age=validated_data.get('age'),
            school=validated_data.get('school', ''),
            location_country=validated_data.get('location_country', ''),
            about_you=validated_data.get('about_you', ''),

        )
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)




