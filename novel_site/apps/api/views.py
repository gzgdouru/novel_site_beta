from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response

from .serializers import EmailCodeSendSerializer, EmailCodeVerifySerializer
from .serializers import MobileCodeSendSerializer, MobileVerifySerializer
from .serializers import PasswdModifySerializer
from users.models import EmailVerify, MobileVerify
from utils.api import send_email_code, send_mobile_code

User = get_user_model()


class EmailCodeSendView(generics.CreateAPIView):
    '''发送邮箱验证码'''
    serializer_class = EmailCodeSendSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        send_type = serializer.validated_data["send_type"]

        err_msg = send_email_code(email, send_type)
        if err_msg:
            return Response({"email": err_msg}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EmailCodeVerifyView(generics.GenericAPIView):
    '''验证邮箱验证码'''
    serializer_class = EmailCodeVerifySerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]
        send_type = serializer.validated_data["send_type"]
        EmailVerify.objects.filter(email=email, code=code, send_type=send_type).update(is_valid=False)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MobileCodeSendView(generics.CreateAPIView):
    '''发送手机验证码'''
    serializer_class = MobileCodeSendSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        mobile = serializer.validated_data["mobile"]
        verify_type = serializer.validated_data["verify_type"]

        err_msg = send_mobile_code(mobile, verify_type)
        if err_msg:
            return Response({"mobile": err_msg}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MobileVerifyView(generics.GenericAPIView):
    '''验证手机验证码'''
    serializer_class = MobileVerifySerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mobile = serializer.validated_data["mobile"]
        code = serializer.validated_data["code"]
        verify_type = serializer.validated_data["verify_type"]
        MobileVerify.objects.filter(mobile=mobile, code=code, verify_type=verify_type).update(is_valid=False)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PasswordModifyView(generics.GenericAPIView):
    '''密码修改'''
    serializer_class = PasswdModifySerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]
        password = make_password(password)
        User.objects.filter(Q(username=username) | Q(email=username) | Q(mobile=username)).update(password=password)
        return Response(serializer.data, status=status.HTTP_200_OK)
