from django.contrib.auth.models import User
from rest_framework import serializers
from api.models import Location
from api.models import Liked


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        print(validated_data)
        user = User.objects.create_user(**validated_data)
        return user
    

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name', 'description','zone','state','city','entryprice']

class LikedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Liked
        fields = ['id', 'user', 'location', 'description']