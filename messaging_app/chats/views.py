# from django.shortcuts import render
from rest_framework import viewsets
from .models import Conversation
from .serializers import ConversationSerializer
from .permissions import IsParticipantOfConversation
# Create your views here.


class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsParticipantOfConversation]

    def get_queryset(self):
        # Good practice: Filter the queryset so users don't even see other's IDs in lists
        return Conversation.objects.filter(participants=self.request.user)