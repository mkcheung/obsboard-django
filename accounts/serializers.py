from django.contrib.auth import (
    get_user_model,
    authenticate,
)

from django.utils.translation import gettext as _
from rest_framework import serializers

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)
    class Meta:
        model = get_user_model()
        fields = ['name', 'email', 'password', 'password_confirm']
        extra_kwargs = {
            'name':{
                'required':True,
                'allow_blank':False,
                'max_length':100,
            },
            'email':{
                'required':True,
                'allow_blank':False,
                'max_length':255
            },
            'password':{
                'required':True,
                'write_only':True,
                'min_length':8
            }
        }

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            name=validated_data['name'],
            email=validated_data['email'],
            username=validated_data["email"],
            password=validated_data['password'],
        )
        return user

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def validate(self, attrs):
        if (attrs['password'] != attrs["password_confirm"]):
            raise serializers.ValidationError("Passwords do not match.")
        return attrs