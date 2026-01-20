# chats/permissions.py
from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Permission to allow only participants of a conversation 
    to view or modify messages within it.
    """

    def has_object_permission(self, request, view, obj):
        # Allow access only if the user is in the conversation's participants
        # This works for Conversation objects
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()
        
        # If the object is a Message, check its parent conversation
        if hasattr(obj, 'conversation'):
            return request.user in obj.conversation.participants.all()
        
        return False