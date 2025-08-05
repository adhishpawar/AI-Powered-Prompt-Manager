from rest_framework import serializers
from django.contrib.auth.models import User

from core.models import PromptHistory, PromptTemplate

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True)

    class Meta:
        model = User
        fields = ['username', 'password','email']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email','')
        
        )

        return user
    

class PromptTemplateSerializers(serializers.ModelSerializer):
    class Meta:
        model = PromptTemplate
        fields = '__all__'
        read_only_fields = ['user', 'created_at']

class PromptHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PromptHistory
        fields = '__all__'
        read_only_fields = ['created_at']