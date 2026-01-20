# messaging_app/chats/views.py
from rest_framework import viewsets,status
from .models import Conversation,Message
from .permissions import IsParticipantOfConversation
from .serializers import (
    ConversationListSerializer, 
    ConversationDetailSerializer,
    MessageSerializer,
    MessageDetailSerializer,
    MessageUpdateSerializer
)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .pagination import MessagePagination
from django_filters.rest_framework import DjangoFilterBackend
from .filters import MessageFilter

class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet to manage user conversations.
    Uses different serializers for list and detail actions.
    """
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

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
    permission_classes = [IsAuthenticated,IsParticipantOfConversation]
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    pagination_class = MessagePagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = MessageFilter

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
    
    def create(self, request, *args, **kwargs):
        """
        Custom create to handle the conversation_id from request data
        and return 403 if the user is not a participant.
        """
        serializer = self.get_serializer(data=request.data)
        
        # This will trigger the validation logic in your MessageSerializer.create
        # which checks if the user belongs to the conversation_id.
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        # If the error is specifically about participation, ensure we return 403
        errors = serializer.errors
        if 'conversation_id' in errors and 'participant' in str(errors['conversation_id']):
            return Response(errors, status=status.HTTP_403_FORBIDDEN)
            
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)