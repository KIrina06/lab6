import ast
import time

from operator import itemgetter
from django.conf import settings
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.core.cache import cache
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt import authentication

from ..jwt_helper import create_access_token, create_refresh_token, get_jwt_payload, get_access_token, get_refresh_token
from ..permissions import *
from ..serializers import *
from ..models import *

access_token_lifetime = settings.JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()
refresh_token_lifetime = settings.JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()

@api_view(["POST"])
def login(request):
    # Ensure email and passwords are posted properly
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Check credentials
    user = authenticate(**serializer.data)
    if user is None:
        message = {"message": "invalid credentials"}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    # Create new access and refresh token
    access_token = create_access_token(user.id)

    # Add access token to redis for validating by other services
    user_data = {
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "is_moderator": user.is_moderator,
        "access_token": access_token
    }
    cache.set(access_token, user_data, access_token_lifetime)

    # Create response object
    response = Response(user_data, status=status.HTTP_201_CREATED)
    # Set access token in cookie
    response.set_cookie('access_token', access_token, httponly=False, expires=access_token_lifetime, samesite="Lax")

    return response


@api_view(["POST"])
def register(request):
    # Ensure username and passwords are posted is properly
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Create user
    user = serializer.save()
    message = {
        'message': 'User registered successfully',
        'user_id': user.id
    }

    return Response(message, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def check(request):
    access_token = get_access_token(request)

    if access_token is None:
        message = {"message": "Token is not found"}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    # Check is token in Redis
    if not cache.has_key(access_token):
        message = {"message": "Token is not valid"}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    user_data = cache.get(access_token)

    return Response(user_data, status=status.HTTP_200_OK)


@api_view(["GET"])
def logout(request):
    access_token = request.COOKIES.get('access_token')

    # Check access token is in cookie
    if access_token is None:
        message = {"message": "Token is not found in cookie"}
        return Response(message, status=status.HTTP_401_UNAUTHORIZED)

    #  Check access token is in Redis
    if cache.has_key(access_token):
        # Delete access token from Redis
        cache.delete(access_token)

    # Create response object
    message = {"message": "Logged out successfully!"}
    response = Response(message, status=status.HTTP_200_OK)
    # Delete access token from cookie
    response.delete_cookie('access_token')

    return response