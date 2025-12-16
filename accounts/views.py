from django.http import JsonResponse
from accounts.serializers import (
    RegisterSerializer,
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return Response({"id": user.id, "name": user.name, "email": user.email}, status=status.HTTP_201_CREATED)

def login(request):
    return JsonResponse({"message": "login endpoint"})

def logout(request):
    return JsonResponse({"message": "logout endpoint"})

def me(request):
    return JsonResponse({"message": "me endpoint"})