from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .serializer import signupSerializer
from .models import signupModel
from rest_framework_simplejwt.tokens import RefreshToken # type: ignore
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
import jwt
import os
import dotenv

# dotenv.load_dotenv()
# @csrf_exempt
# def Verify_token(request,token):
#     if request.method == 'GET':
#         try:
#             verifyToken = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms='HS256')
#             print(verifyToken)
#         #     return verifyToken

#         except Exception as e:
#             print('error: ',e)

dotenv.load_dotenv()

# Helper function to verify JWT token
def verify_token(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        return None, JsonResponse({'status': 'error', 'message': 'Missing or invalid token'}, status=401)

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=['HS256'])
        user_id = payload.get('user_id')
        return user_id, None
    except jwt.ExpiredSignatureError:
        return None, JsonResponse({'status': 'error', 'message': 'Token has expired'}, status=401)
    except jwt.InvalidTokenError:
        return None, JsonResponse({'status': 'error', 'message': 'Invalid token'}, status=401)


@csrf_exempt
@require_POST
def signUp(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            serializer = signupSerializer(data=data)
            if serializer.is_valid():
                user = serializer.save()
                refresh = RefreshToken.for_user(user)
                access_token = refresh.access_token
                access_token['username'] = user.username
                response_data = {
                    'refresh_token':str(refresh),
                    'access_token': str(access_token),
                }
                return JsonResponse(response_data, status=201)
            else:
                return JsonResponse({'error':'Email already used !'}, status=400)
        except Exception as e:
            return JsonResponse({'error':str(e)},status=500)


@csrf_exempt
@require_POST
def login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return JsonResponse(
                    {'error': 'Email and password are required!'},
                    status=400
                )
            
            # Check if the user exists
            try:
                isUser = signupModel.objects.get(email=email)
            except signupModel.DoesNotExist:

                return JsonResponse({'error':'User does not exist!'}, status=404)
                
            user = authenticate(request, email=email, password=password)
            if user is not None:
                auth_login(request, user)
                refresh = RefreshToken.for_user(user)
                access_token = refresh.access_token
                access_token['username'] = user.username
                Response_data = {
                    'refresh_token':str(refresh),
                    'access_token':str(access_token),
                }
                return JsonResponse(Response_data, status=200)
            else:
                return JsonResponse({'error':'invalid credentials!'}, status=401)
        except :
            return JsonResponse({'error': 'An unexpected error occurred. Please try again later.'},status=500)
        

