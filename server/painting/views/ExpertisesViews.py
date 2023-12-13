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

@api_view(["GET"])
def get_expertises(request):
    expertises = Expertises.objects.all()
    serializer = ExpertiseSerializer(expertises, many=True)

    return Response(serializer.data)

@api_view(["GET"])
def get_expertise_by_id(request, expertise_id):
    if not Expertises.objects.filter(pk=expertise_id).exists():
        return Response(f"Экспертизы с таким id не существует!")

    expertise = Expertises.objects.get(pk=expertise_id)
    serializer = ExpertiseSerializer(expertise, many=False)

    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsModerator])
def create_expertise(request):
    Expertises.objects.create()

    expertises = Expertises.objects.all()
    serializer = ExpertiseSerializer(expertises, many=True)
    return Response(serializer.data)

@api_view(["PUT"])
@permission_classes([IsModerator])
def update_expertise(request, expertise_id):
    if not Expertises.objects.filter(pk=expertise_id).exists():
        return Response(f"Экспертизы с таким id не существует!")

    expertise = Expertises.objects.get(pk=expertise_id)
    serializer = ExpertiseSerializer(expertise, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_expertise(request, expertise_id):
    if not Expertises.objects.filter(pk=expertise_id).exists():
        return Response(f"Экспертизы с таким id не существует!")

    expertise = Expertises.objects.get(pk=expertise_id)
    expertise.expertise_status = 2
    expertise.save()

    expertises = Expertises.objects.filter(expertise_status=1)
    serializer = ExpertiseSerializer(expertises, many=True)
    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_expertise_to_request(request, expertise_id):

    token = get_access_token(request)
    payload = get_jwt_payload(token)
    user_id = payload["user_id"]

    if not Expertises.objects.filter(pk=expertise_id).exists():
        return Response(f"Экспертизы с таким id не существует!")

    expertise = Expertises.objects.get(pk=expertise_id)

    req = Requests.objects.filter(req_status=1).last()

    if req is None:
        req = Requests.objects.create()

    req.expertises.add(expertise)
    req.user = CustomUser.objects.get(pk=payload["user_id"])
    req.save()

    serializer = ExpertiseSerializer(req.expertises, many=True)
    return Response(serializer.data)
