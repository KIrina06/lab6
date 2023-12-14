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
@permission_classes([IsAuthenticated])
def get_requests(request):
    token = get_access_token(request)
    payload = get_jwt_payload(token)
    user_id = payload["user_id"]

    requests = Requests.objects.filter(user_id=user_id).exclude(req_status__in=[5])
    serializer = RequestSerializer(requests, many=True)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_request_by_id(request, request_id):
    if not Requests.objects.filter(pk=request_id).exists():
        return Response(f"Заявки с таким id не существует!")

    req = Requests.objects.get(pk=request_id)
    serializer = RequestSerializer(req, many=False)
    return Response(serializer.data)

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_request(request, request_id):
    if not Requests.objects.filter(pk=request_id).exists():
        return Response(f"Заявки с таким id не существует!")

    req = Requests.objects.get(pk=request_id)
    serializer = RequestSerializer(req, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    req.req_status = 1
    req.save()

    return Response(serializer.data)

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_request_user(request, request_id):
    if not Requests.objects.filter(pk=request_id).exists():
        return Response(f"Заявки с таким id не существует!")

    request_status = request.data["req_status"]

    if request_status not in [1, 5]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    req = Requests.objects.get(pk=request_id)
    req_status = req.req_status

    if req_status == 5:
        return Response("Статус изменить нельзя")

    req.req_status = request_status
    req.save()

    serializer = RequestSerializer(req, many=False)
    return Response(serializer.data)

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_request_admin(request, request_id):
    if not Requests.objects.filter(pk=request_id).exists():
        return Response(f"Заявки с таким id не существует!")

    request_status = request.data["req_status"]

    if request_status in [1, 5]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    req = Requests.objects.get(pk=request_id)

    req_status = req.req_status

    if req_status in [3, 4, 5]:
        return Response("Статус изменить нельзя")

    req.req_status = request_status
    req.save()

    serializer = RequestSerializer(req, many=False)
    return Response(serializer.data)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_request(request, request_id):
    token = get_access_token(request)
    payload = get_jwt_payload(token)
    user_id = payload["user_id"]

    if not Requests.objects.filter(pk=request_id, user__pk=user_id).exists():
        return Response(f"Заявки с таким id не существует!")

    req = Requests.objects.get(pk=request_id)
    req.req_status = 5
    req.save()

    requests = Requests.objects.filter(user_id=user_id).exclude(req_status__in=[5])
    serializer = RequestSerializer(requests, many=True)
    return Response(serializer.data)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_expertise_from_request(request, request_id, expertise_id):
    if not Requests.objects.filter(pk=request_id).exists():
        return Response(f"Заявки с таким id не существует")

    if not Expertises.objects.filter(pk=expertise_id).exists():
        return Response(f"Экспертизы с таким id не существует")

    req = Requests.objects.get(pk=request_id)
    req.expertises.remove(Expertises.objects.get(pk=expertise_id))
    req.save()

    serializer = ExpertiseSerializer(req.expertises, many=True)
    return Response(serializer.data)

@api_view(["PUT"])
@permission_classes([IsInternal])
def update_request_internal(request, request_id):
    if not Requests.objects.filter(pk=request_id).exists():
        return Response(f"Заявки с таким id не существует!", status=status.HTTP_404_NOT_FOUND)

    request_status = request.data["req_status"]

    if request_status not in range(1, 6):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    req = Requests.objects.get(pk=request_id)
    req.req_status = request_status
    req.save()

    serializer = RequestSerializer(req, many=False)
    return Response(serializer.data)
