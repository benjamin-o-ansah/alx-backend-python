# messaging_app/chats/views.py
from rest_framework import viewsets
from .models import Conversation,Message
from .permissions import IsParticipantOfConversation
from .serializers import (
    ConversationListSerializer, 
    ConversationDetailSerializer,
    MessageSerializer,
    MessageDetailSerializer,
    MessageUpdateSerializer
)

class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet to manage user conversations.
    Uses different serializers for list and detail actions.
    """
    permission_classes = [IsParticipantOfConversation]

    def get_queryset(self):
        # Optimize with prefetch_related to avoid N+1 queries 
        # when fetching participants and messages
        return Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related('participants', 'messages')

    def get_serializer_class(self):
        # Switch serializer based on the current action
        if self.action == 'list':
            return ConversationListSerializer
        if self.action in ['retrieve', 'update', 'partial_update']:
            return ConversationDetailSerializer
        return ConversationListSerializer # Default fallback (e.g., for 'create')
    
class MessageViewSet(viewsets.ModelViewSet):
    """
    Handles Listing, Creating, and Updating (read status) Messages.
    """
    permission_classes = [IsParticipantOfConversation]

    def get_queryset(self):
        # Optimized with select_related for sender info
        return Message.objects.filter(
            conversation__participants=self.request.user
        ).select_related('sender', 'conversation')

    def get_serializer_class(self):
        # Use MessageDetailSerializer for single object view
        if self.action == 'retrieve':
            return MessageDetailSerializer
        
        # Use MessageUpdateSerializer for PUT/PATCH actions (like marking as read)
        if self.action in ['update', 'partial_update']:
            return MessageUpdateSerializer
        
        # Default to the main MessageSerializer for 'list' and 'create'
        return MessageSerializer