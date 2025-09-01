from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework.views import APIView
from django.contrib.auth import update_session_auth_hash
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse
from drf_spectacular.openapi import OpenApiTypes
from .serializers import (
    CustomTokenObtainPairSerializer,
    NguoiDungRegistrationSerializer,
    NguoiDungSerializer,
    ChangePasswordSerializer
)
from .models import NguoiDung
import logging

logger = logging.getLogger(__name__)

@extend_schema(
    operation_id='auth_login',
    tags=['Authentication'],
    summary='User login',
    description='Authenticate user with phone number and password, returns JWT tokens',
    request=CustomTokenObtainPairSerializer,
    responses={
        200: OpenApiResponse(
            description='Login successful',
            response={
                'type': 'object',
                'properties': {
                    'access': {'type': 'string', 'description': 'JWT access token'},
                    'refresh': {'type': 'string', 'description': 'JWT refresh token'},
                    'user': {
                        'type': 'object',
                        'properties': {
                            'ma_nguoi_dung': {'type': 'integer'},
                            'so_dien_thoai': {'type': 'string'},
                            'vai_tro': {'type': 'string'},
                            'trang_thai': {'type': 'string'}
                        }
                    }
                }
            }
        ),
        400: OpenApiResponse(
            description='Bad request - Invalid input data',
            response={
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'description': 'Error message'},
                    'details': {'type': 'object', 'description': 'Field-specific errors'}
                }
            }
        ),
        401: OpenApiResponse(
            description='Unauthorized - Invalid credentials',
            response={
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'description': 'Authentication error message'}
                }
            }
        ),
        429: OpenApiResponse(
            description='Too many requests - Rate limit exceeded',
            response={
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'description': 'Rate limit error message'}
                }
            }
        ),
        500: OpenApiResponse(
            description='Internal server error',
            response={
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'description': 'Server error message'}
                }
            }
        )
    }
)
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        try:
            # Validate input data
            if not request.data:
                logger.warning("Empty request data for login attempt")
                return Response(
                    {'error': 'Request body is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check required fields
            required_fields = ['so_dien_thoai', 'mat_khau']
            missing_fields = [field for field in required_fields if not request.data.get(field)]
            if missing_fields:
                logger.warning(f"Missing required fields in login: {missing_fields}")
                return Response(
                    {
                        'error': 'Missing required fields',
                        'details': {field: 'This field is required' for field in missing_fields}
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Use the serializer directly since it handles the entire authentication
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                logger.info(f"Successful login for user: {request.data.get('so_dien_thoai')}")
                return Response(serializer.validated_data, status=status.HTTP_200_OK)
            else:
                logger.warning(f"Login failed for phone: {request.data.get('so_dien_thoai', 'unknown')}")
                return Response(
                    {
                        'error': 'Invalid credentials',
                        'details': serializer.errors
                    },
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
        except ValidationError as e:
            logger.error(f"Validation error in login: {str(e)}")
            return Response(
                {'error': 'Invalid input data', 'details': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except TokenError as e:
            logger.error(f"Token error in login: {str(e)}")
            return Response(
                {'error': 'Token generation failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"Unexpected error in login: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(
    operation_id='auth_refresh_token',
    tags=['Authentication'],
    summary='Refresh JWT token',
    description='Get a new access token using refresh token',
    request={
        'type': 'object',
        'properties': {
            'refresh': {'type': 'string', 'description': 'Refresh token'}
        },
        'required': ['refresh']
    },
    responses={
        200: OpenApiResponse(
            description='Token refresh successful',
            response={
                'type': 'object',
                'properties': {
                    'access': {'type': 'string', 'description': 'New JWT access token'}
                }
            }
        ),
        400: OpenApiResponse(
            description='Bad request - Invalid refresh token format',
            response={
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'description': 'Error message'}
                }
            }
        ),
        401: OpenApiResponse(
            description='Unauthorized - Invalid or expired refresh token',
            response={
                'type': 'object',
                'properties': {
                    'detail': {'type': 'string', 'description': 'Token error message'}
                }
            }
        )
    }
)
class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        try:
            if not request.data or not request.data.get('refresh'):
                logger.warning("Missing refresh token in request")
                return Response(
                    {'error': 'Refresh token is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            response = super().post(request, *args, **kwargs)
            
            if response.status_code == 200:
                logger.info("Token refresh successful")
            else:
                logger.warning("Token refresh failed")
                
            return response
            
        except InvalidToken as e:
            logger.error(f"Invalid refresh token: {str(e)}")
            return Response(
                {'error': 'Invalid or expired refresh token'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            logger.error(f"Unexpected error in token refresh: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(
    operation_id='auth_verify_token',
    tags=['Authentication'],
    summary='Verify JWT token',
    description='Verify if a JWT token is valid',
    request={
        'type': 'object',
        'properties': {
            'token': {'type': 'string', 'description': 'JWT token to verify'}
        },
        'required': ['token']
    },
    responses={
        200: OpenApiResponse(
            description='Token is valid',
            response={'type': 'object', 'properties': {}}
        ),
        400: OpenApiResponse(
            description='Bad request - Missing token',
            response={
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'description': 'Error message'}
                }
            }
        ),
        401: OpenApiResponse(
            description='Unauthorized - Invalid token',
            response={
                'type': 'object',
                'properties': {
                    'detail': {'type': 'string', 'description': 'Token validation error'}
                }
            }
        )
    }
)
class CustomTokenVerifyView(TokenVerifyView):
    def post(self, request, *args, **kwargs):
        try:
            if not request.data or not request.data.get('token'):
                logger.warning("Missing token in verify request")
                return Response(
                    {'error': 'Token is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            response = super().post(request, *args, **kwargs)
            
            if response.status_code == 200:
                logger.info("Token verification successful")
            else:
                logger.warning("Token verification failed")
                
            return response
            
        except InvalidToken as e:
            logger.error(f"Invalid token in verification: {str(e)}")
            return Response(
                {'detail': 'Token is invalid or expired'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            logger.error(f"Unexpected error in token verification: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    post=extend_schema(
        operation_id='auth_register',
        tags=['Authentication'],
        summary='User registration',
        description='Register a new user account',
        request=NguoiDungRegistrationSerializer,
        responses={201: NguoiDungSerializer}
    )
)
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = NguoiDungRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'Đăng ký thành công',
                'user': NguoiDungSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    get=extend_schema(
        operation_id='auth_profile_get',
        tags=['Authentication'],
        summary='Get user profile',
        description='Get current user profile information',
        responses={200: NguoiDungSerializer}
    ),
    patch=extend_schema(
        operation_id='auth_profile_update',
        tags=['Authentication'],
        summary='Update user profile',
        description='Update current user profile information',
        request=NguoiDungSerializer,
        responses={200: NguoiDungSerializer}
    )
)
class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = NguoiDungSerializer(request.user)
        return Response(serializer.data)
    
    def patch(self, request):
        serializer = NguoiDungSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    post=extend_schema(
        operation_id='auth_change_password',
        tags=['Authentication'],
        summary='Change password',
        description='Change user password',
        request=ChangePasswordSerializer,
        responses={200: {'type': 'object', 'properties': {'message': {'type': 'string'}}}}
    )
)
class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            
            # Kiểm tra mật khẩu cũ
            if not user.check_password(serializer.validated_data['mat_khau_cu']):
                return Response({
                    'mat_khau_cu': ['Mật khẩu cũ không đúng.']
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Đổi mật khẩu
            user.set_password(serializer.validated_data['mat_khau_moi'])
            user.save()
            
            # Cập nhật session
            update_session_auth_hash(request, user)
            
            return Response({
                'message': 'Đổi mật khẩu thành công'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    operation_id='auth_check_permissions',
    tags=['Authentication'],
    summary='Check user permissions',
    description='Get current user role and permissions',
    responses={200: {
        'type': 'object',
        'properties': {
            'vai_tro': {'type': 'string'},
            'is_admin': {'type': 'boolean'},
            'is_doctor': {'type': 'boolean'},
            'is_patient': {'type': 'boolean'},
            'is_staff': {'type': 'boolean'},
            'trang_thai': {'type': 'string'}
        }
    }}
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_permission(request):
    """Kiểm tra quyền của user hiện tại"""
    user = request.user
    permissions_data = {
        'vai_tro': user.vai_tro,
        'is_admin': user.vai_tro == 'Admin',
        'is_doctor': user.vai_tro == 'Bác sĩ',
        'is_patient': user.vai_tro == 'Bệnh nhân',
        'is_staff': user.vai_tro == 'Nhân viên',
        'trang_thai': user.trang_thai
    }
    return Response(permissions_data)
