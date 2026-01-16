import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from datetime import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver



class User(AbstractUser):
    """User model extending Django's AbstractUser"""
    
    # Using UUID as primary key
    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    
    # Override default fields to match specification
    first_name = models.CharField(max_length=150, null=False, blank=False)
    last_name = models.CharField(max_length=150, null=False, blank=False)
    email = models.EmailField(unique=True, null=False, blank=False, db_index=True)
    
    # Password field is already handled by AbstractUser as 'password'
    
    # Phone number with validation
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True
    )
    
    # Role choices
    class Role(models.TextChoices):
        GUEST = 'guest', 'Guest'
        HOST = 'host', 'Host'
        ADMIN = 'admin', 'Admin'
    
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.GUEST,
        null=False,
        blank=False
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Override username field to use email
    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        db_table = 'user'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['email'], name='unique_user_email'),
        ]
    
    def __str__(self):
        return f"{self.email} - {self.get_full_name()}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
class Conversation(models.Model):
    """Conversation model to track conversations between users"""
    
    conversation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    
    # Many-to-many relationship for participants
    # This allows conversations with multiple users
    participants = models.ManyToManyField(
        User,
        related_name='conversations',
        db_index=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'conversation'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        participant_names = ", ".join([
            user.get_full_name() 
            for user in self.participants.all()[:3]
        ])
        return f"Conversation {self.conversation_id} - Participants: {participant_names}"
    
    def add_participant(self, user):
        """Helper method to add a participant to the conversation"""
        self.participants.add(user)
    
    def remove_participant(self, user):
        """Helper method to remove a participant from the conversation"""
        self.participants.remove(user)
    
    def get_participants_count(self):
        """Get the number of participants in the conversation"""
        return self.participants.count()
    
class MessageManager(models.Manager):
    """Custom manager for Message model"""
    
    def get_unread_count(self, user):
        """Get count of unread messages for a user"""
        return self.filter(
            conversation__participants=user,
            is_read=False
        ).exclude(sender=user).count()
    
    def get_conversation_messages(self, conversation_id, user):
        """Get messages for a specific conversation"""
        return self.filter(
            conversation_id=conversation_id,
            conversation__participants=user
        ).select_related('sender').order_by('sent_at')
    
class Message(models.Model):
    """Message model for storing individual messages in conversations"""
    objects = MessageManager()
    message_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        db_index=True
    )
    
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        db_index=True
    )
    
    message_body = models.TextField(null=False, blank=False)
    
    sent_at = models.DateTimeField(auto_now_add=True)
    
    # Optional: Add read status if needed
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Optional: Add message type if needed (text, image, etc.)
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('file', 'File'),
    ]
    message_type = models.CharField(
        max_length=10,
        choices=MESSAGE_TYPE_CHOICES,
        default='text'
    )
    
    # Optional: For file attachments
    attachment = models.FileField(
        upload_to='message_attachments/',
        null=True,
        blank=True
    )

    
    
    class Meta:
        db_table = 'message'
        ordering = ['sent_at']
        indexes = [
            models.Index(fields=['sender', 'sent_at']),
            models.Index(fields=['conversation', 'sent_at']),
            models.Index(fields=['sent_at']),
            models.Index(fields=['is_read']),
        ]
    
    def __str__(self):
        return f"Message from {self.sender.email} at {self.sent_at}"
    
    def mark_as_read(self):
        """Mark the message as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = datetime.tzname.now()
            self.save()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Signal to create user profile when a new user is created"""
    if created:
        # You can add additional profile creation logic here
        pass

class MessageManager(models.Manager):
    """Custom manager for Message model"""
    
    def get_unread_count(self, user):
        """Get count of unread messages for a user"""
        return self.filter(
            conversation__participants=user,
            is_read=False
        ).exclude(sender=user).count()
    
    def get_conversation_messages(self, conversation_id, user):
        """Get messages for a specific conversation"""
        return self.filter(
            conversation_id=conversation_id,
            conversation__participants=user
        ).select_related('sender').order_by('sent_at')