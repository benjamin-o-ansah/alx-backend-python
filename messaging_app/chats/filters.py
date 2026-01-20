# chats/filters.py
import django_filters
from .models import Message

class MessageFilter(django_filters.FilterSet):
    # Filter by specific users involved (sender or participants in conversation)
    sender_email = django_filters.CharFilter(field_name='sender__email', lookup_expr='icontains')
    
    # Filter by time range
    start_date = django_filters.DateTimeFilter(field_name='sent_at', lookup_expr='gte')
    end_date = django_filters.DateTimeFilter(field_name='sent_at', lookup_expr='lte')

    class Meta:
        model = Message
        fields = ['sender_email', 'start_date', 'end_date']