# chats/permissions.py
from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Permission to allow only participants of a conversation 
    to view or modify messages within it.
    """

    def has_permission(self, request, view):
        # 1. First Gatekeeper: Only logged-in users get past this point
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        # Determine if we are dealing with a Conversation or a Message
        is_message = hasattr(obj, 'conversation')
        conversation = obj.conversation if is_message else obj

        # Verify the user is a participant of the conversation
        is_participant = conversation.participants.filter(user_id=request.user.user_id).exists()

        if not is_participant:
            return False

        # Apply stricter logic for Unsafe Methods (PUT, PATCH, DELETE) on Messages
        if is_message and request.method in ['PUT', 'PATCH', 'DELETE']:
            # Only the sender of the message can modify or delete it
            return obj.sender == request.user

        # For GET, HEAD, or OPTIONS, being a participant is enough
        return request.user in obj.conversation.participants.all()