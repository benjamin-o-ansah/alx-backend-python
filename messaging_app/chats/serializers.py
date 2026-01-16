from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, Conversation, Message
from rest_framework.pagination import PageNumberPagination

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
    

class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model"""
    
    sender = serializers.SlugRelatedField(
        slug_field='email',
        read_only=True
    )
    sender_details = serializers.SerializerMethodField()
    conversation_id = serializers.UUIDField(write_only=True, required=True)
    
    class Meta:
        model = Message
        fields = [
            'message_id', 'sender', 'sender_details',
            'conversation_id', 'conversation',
            'message_body', 'message_type', 'attachment',
            'is_read', 'read_at', 'sent_at'
        ]
        read_only_fields = [
            'message_id', 'sender', 'sender_details',
            'conversation', 'is_read', 'read_at', 'sent_at'
        ]
        extra_kwargs = {
            'conversation': {'read_only': True},
        }
    
    def get_sender_details(self, obj):
        """Get simplified sender details"""
        return {
            'user_id': str(obj.sender.user_id),
            'email': obj.sender.email,
            'full_name': obj.sender.get_full_name(),
            'role': obj.sender.role
        }
    
    def create(self, validated_data):
        """Create a new message"""
        # Extract conversation_id from validated data
        conversation_id = validated_data.pop('conversation_id')
        
        # Get the conversation
        try:
            conversation = Conversation.objects.get(
                conversation_id=conversation_id,
                participants=self.context['request'].user
            )
        except Conversation.DoesNotExist:
            raise serializers.ValidationError({
                'conversation_id': 'Conversation not found or you are not a participant.'
            })
        
        # Create message
        message = Message.objects.create(
            sender=self.context['request'].user,
            conversation=conversation,
            **validated_data
        )
        
        return message


class MessageDetailSerializer(MessageSerializer):
    """Detailed serializer for Message with more sender info"""
    
    class Meta(MessageSerializer.Meta):
        fields = MessageSerializer.Meta.fields


class MessageUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating message (mainly read status)"""
    
    class Meta:
        model = Message
        fields = ['is_read']
        
    def update(self, instance, validated_data):
        """Update message read status"""
        is_read = validated_data.get('is_read', instance.is_read)
        
        if is_read and not instance.is_read:
            instance.mark_as_read()
        elif not is_read:
            instance.is_read = False
            instance.read_at = None
            instance.save()
        
        return instance
    
class ConversationListSerializer(serializers.ModelSerializer):
    """Serializer for listing conversations"""
    
    participants = UserDetailSerializer(many=True, read_only=True)
    participants_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id', 'participants', 'participants_ids',
            'last_message', 'unread_count', 'created_at'
        ]
        read_only_fields = ['conversation_id', 'participants', 'created_at']
    
    def get_last_message(self, obj):
        """Get the last message in the conversation"""
        last_message = obj.messages.order_by('-sent_at').first()
        if last_message:
            return {
                'message_id': str(last_message.message_id),
                'sender': last_message.sender.email,
                'message_body': last_message.message_body[:100],  # Preview
                'sent_at': last_message.sent_at,
                'is_read': last_message.is_read
            }
        return None
    
    def get_unread_count(self, obj):
        """Get count of unread messages for the current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(
                is_read=False
            ).exclude(
                sender=request.user
            ).count()
        return 0
    
    def validate_participants_ids(self, value):
        """Validate participant IDs"""
        if len(value) < 2:
            raise serializers.ValidationError(
                'A conversation must have at least 2 participants.'
            )
        
        # Check if all users exist
        existing_users = User.objects.filter(user_id__in=value)
        if len(existing_users) != len(value):
            raise serializers.ValidationError(
                'One or more users do not exist.'
            )
        
        return value
    
    def create(self, validated_data):
        """Create a conversation with participants"""
        participants_ids = validated_data.pop('participants_ids', [])
        
        # Include the current user in participants if not already included
        request = self.context.get('request')
        current_user_id = request.user.user_id if request and request.user.is_authenticated else None
        
        if current_user_id and current_user_id not in participants_ids:
            participants_ids.append(current_user_id)
        
        # Create conversation
        conversation = Conversation.objects.create()
        
        # Add participants
        users = User.objects.filter(user_id__in=participants_ids)
        conversation.participants.set(users)
        
        return conversation


class ConversationDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Conversation with messages"""
    
    participants = UserDetailSerializer(many=True, read_only=True)
    messages = serializers.SerializerMethodField()
    pagination_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id', 'participants', 'messages',
            'pagination_info', 'created_at'
        ]
        read_only_fields = fields
    
    def get_messages(self, obj):
        """Get paginated messages for the conversation"""
        request = self.context.get('request')
        page_size = request.query_params.get('page_size', 20) if request else 20
        
        try:
            page_size = int(page_size)
        except ValueError:
            page_size = 20
        
        # Get messages
        messages = obj.messages.select_related('sender').order_by('-sent_at')
        
        # Paginate
        paginator = self.context.get('paginator')
        if paginator:
            page = paginator.page
            paginated_messages = paginator.paginate_queryset(messages, request)
            return MessageSerializer(paginated_messages, many=True, context=self.context).data
        
        # If no paginator, return recent messages
        recent_messages = messages[:page_size]
        return MessageSerializer(recent_messages, many=True, context=self.context).data
    
    def get_pagination_info(self, obj):
        """Get pagination information"""
        request = self.context.get('request')
        if not request:
            return None
        
        paginator = self.context.get('paginator')
        if paginator:
            return {
                'count': paginator.count,
                'total_pages': paginator.num_pages,
                'current_page': paginator.page.number,
                'page_size': paginator.page_size,
                'next': paginator.get_next_link(),
                'previous': paginator.get_previous_link(),
            }
        return None
    
class UserConversationSerializer(serializers.ModelSerializer):
    """Serializer for user conversations with last message"""
    
    conversation_id = serializers.UUIDField(source='user_id', read_only=True)
    last_message = serializers.SerializerMethodField()
    other_participants = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'conversation_id', 'email', 'first_name', 'last_name',
            'full_name', 'last_message', 'other_participants'
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_last_message(self, obj):
        # This would need custom logic to get the last message
        # between the current user and this user
        return None
    
    def get_other_participants(self, obj):
        return []


class ConversationWithMessagesSerializer(ConversationDetailSerializer):
    """Alternative conversation serializer with inline messages"""
    
    class Meta(ConversationDetailSerializer.Meta):
        fields = ConversationDetailSerializer.Meta.fields


class UserWithConversationsSerializer(UserDetailSerializer):
    """User serializer with their conversations"""
    
    conversations = ConversationListSerializer(
        source='conversations.all',
        many=True,
        read_only=True
    )
    
    class Meta(UserDetailSerializer.Meta):
        fields = UserDetailSerializer.Meta.fields + ['conversations']

class MessagePagination(PageNumberPagination):
    """Custom pagination for messages"""
    
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return {
            'pagination': {
                'count': self.page.paginator.count,
                'total_pages': self.page.paginator.num_pages,
                'current_page': self.page.number,
                'page_size': self.page.paginator.per_page,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
            },
            'messages': data
        }