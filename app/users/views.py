from users.models import User
from rest_framework import permissions
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.response import Response
from users.serializers import RegisterSerializer
from rest_framework import generics
import json

def obtain_auth_token_via_nonce(request):
    body = json.loads(request.body)
    body['signature']
    user = User.objects.get(public_address=body['public_address'])
    msg = "I am signing my one-time nonce: {}".format(user.nonce)
    message_hash = defunct_hash_message(text=message)
    address = w3.eth.account.recoverHash(message_hash, signature=signature)
    return address


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        token, created = Token.objects.get_or_create(user=serializer.instance)
        return Response({'token': token.key}, status=status.HTTP_201_CREATED, headers=headers)


class UserView(generics.GenericAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email
        }, status=status.HTTP_200_OK)
