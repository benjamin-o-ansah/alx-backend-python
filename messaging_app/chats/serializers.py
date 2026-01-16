from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, Conversation, Message


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users"""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirmation = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'user_id', 'first_name', 'last_name', 'email',
            'phone_number', 'role', 'password', 'password_confirmation',
            'created_at'
        ]
        read_only_fields = ['user_id', 'created_at']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
        }
    
    def validate(self, data):
        """Validate that passwords match"""
        if data['password'] != data['password_confirmation']:
            raise serializers.ValidationError({
                'password_confirmation': 'Passwords do not match.'
            })
        return data
    
    def create(self, validated_data):
        """Create a new user with encrypted password"""
        # Remove password_confirmation from validated data
        validated_data.pop('password_confirmation', None)
        
        # Create user
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data.get('phone_number'),
            role=validated_data.get('role', User.Role.GUEST)
        )
        
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user details"""
    
    class Meta:
        model = User
        fields = [
            'user_id', 'first_name', 'last_name', 'email',
            'phone_number', 'role', 'created_at'
        ]
        read_only_fields = ['user_id', 'email', 'created_at']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }


class UserDetailSerializer(serializers.ModelSerializer):
    """Serializer for user detail view"""
    
    full_name = serializers.SerializerMethodField()
    conversation_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'user_id', 'first_name', 'last_name', 'full_name',
            'email', 'phone_number', 'role', 'created_at',
            'conversation_count'
        ]
        read_only_fields = fields
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_conversation_count(self, obj):
        return obj.conversations.count()


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user authentication"""
    
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True
    )
    
    def validate(self, data):
        """Validate user credentials"""
        email = data.get('email')
        password = data.get('password')
        
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError(
                    'Unable to log in with provided credentials.'
                )
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
        else:
            raise serializers.ValidationError(
                'Must include "email" and "password".'
            )
        
        data['user'] = user
        return data


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change"""
    
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password]
    )
    new_password_confirmation = serializers.CharField(
        required=True,
        write_only=True
    )
    
    def validate(self, data):
        """Validate passwords"""
        # Check if new passwords match
        if data['new_password'] != data['new_password_confirmation']:
            raise serializers.ValidationError({
                'new_password_confirmation': 'Passwords do not match.'
            })
        
        # Check if old password is correct
        user = self.context['request'].user
        if not user.check_password(data['old_password']):
            raise serializers.ValidationError({
                'old_password': 'Old password is incorrect.'
            })
        
        # Check if new password is different from old password
        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError({
                'new_password': 'New password must be different from old password.'
            })
        
        return data
    
    def save(self, **kwargs):
        """Save new password"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
    

