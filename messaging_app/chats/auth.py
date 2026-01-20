from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Customizes the JWT payload to include user-specific data.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims (these will be encoded in the JWT)
        token['username'] = user.username
        token['email'] = user.email
        # You can add more fields if needed for your messaging app
        
        return token

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom view to use the custom serializer.
    """
    serializer_class = CustomTokenObtainPairSerializer