#from django.shortcuts import render
#from datetime import datetime

#from django.conf import settings

#import redis
#from Universe.yasg import schema_view
#from rest_framework import status
#from rest_framework.permissions import IsAuthenticated
#from rest_framework.response import Response
#from rest_framework.views import APIView

#from universeShops.permissions import IsAnonymoused
#from .models import User
#from .tasks import  send_sms_user_register, send_sms_forget_password
#from .serializers import UseregisterSerializer, UserForgetSerializer,\
  #  UniqueValidator, UserVerificationSerializer, UserVerificationPasswordSerializer, \
 #   UserChangePasswordSerializer, UserEditProfileSerializer

#class UserRegisterView(APIView):
    #"""
     #   get user and send sms for verification phone number
    #"""
    #serializers_class = UseregisterSerializer
    #permission_classes = (
     #   IsAnonymoused,
    #)

   # @schema_view(request_body = serializers_class)
   # def post(self, request):
    #    srz_data = self.serializers_class(data = request.data)
   #     if srz_data.is_valid(raise_exception=True):
  #          request.session['phone_register'] = srz_data.validated_data['phone']
 #           send_sms_user_register.delay(srz_data.validated_data)
#            return Response(data = {'message': 'sms send.'}, status=status.HTTP_200_OK)


#class UserVerificationView(APIView):
    #"""
      #  Check user otp code and create new user
    #"""

    #serializer_class = UserVerificationSerializer
    #permission_classes = (
     #   IsAnonymoused,
    #)

    #@schema_view(request_body = serializer_class)
    #def post(self, request):
       # srz_data = self.serializer_class(data = request.data)
       # if srz_data.is_valid(raise_exception=True):
           # redis_con = redis.Redis(host = settings.REDIS_HOST, port = settings.REDIS_PORT, db = settings.PHONE_REGISTER_DB)
           # code = srz_data.validated_data['code']
            #if redis_con.exists(request.session.get('phone_register', 'no_phone')):
               # user_data = redis_con.hgetall(request.session['phone_register'])
               # if code == int(user_data.get(b'otp_code')):
               #     User.objects.create_user(
              #          phone = (request.session['phone_register']),
             #           name = (user_data[b'name'].data
            #        )


