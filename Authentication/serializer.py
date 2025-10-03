from rest_framework import serializers
from .models import signupModel

class signupSerializer(serializers.ModelSerializer):
    class Meta:
        model = signupModel
        fields = ('username', 'email','password')

    def create(self, validated_data):
        user = signupModel.objects.create_user(
            username = validated_data['username'],
            email = validated_data['email'],
            password = validated_data['password']
        )
        return user