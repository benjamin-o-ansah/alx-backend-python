from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to view it.
    """
    def has_object_permission(self, request, view, obj):
        # Assuming your Conversation model has a many-to-many 'participants' field
        # or your Message model has a 'sender'/'receiver' field.
        return request.user in obj.participants.all()

class IsMessageOwner(permissions.BasePermission):
    """
    Custom permission to only allow the sender of a message to edit/delete it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.sender == request.user