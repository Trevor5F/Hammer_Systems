from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone_number', 'auth_code', 'invite_code', 'activated_invite_code']

    def create(self, validated_data):
        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.auth_code = validated_data.get('auth_code', instance.auth_code)
        instance.invite_code = validated_data.get('invite_code', instance.invite_code)
        instance.activated_invite_code = validated_data.get('activated_invite_code', instance.activated_invite_code)
        instance.save()
        return instance
