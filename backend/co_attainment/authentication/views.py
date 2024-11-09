from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created

from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import *
from .models import EmailOTP

from random import randint


@receiver(reset_password_token_created)
def password_reset_token_created(instance, reset_password_token, *args, **kwargs):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    :param args:
    :param kwargs:
    :return:
    """
    # send an e-mail to the user
    context = {
        'current_user': reset_password_token.user,
        'email': reset_password_token.user.email,
        'reset_password_url': "{}?token={}".format(
            instance.request.build_absolute_uri(reverse('authentication:password_reset:reset-password-confirm')),
            reset_password_token.key
        )
    }

    # render email text
    email_html_message = render_to_string('email/user_reset_password.html', context)
    email_plaintext_message = render_to_string('email/user_reset_password.txt', context)

    msg = EmailMultiAlternatives(
        # title:
        "Password Reset for {title}".format(title="CO Attainment Portal"),
        # message:
        email_plaintext_message,
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [reset_password_token.user.email]
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()

class EmailOTPGenerationAPIView(APIView):
    permission_classes = (permissions.AllowAny, )
    def post(self, request):
        email = request.data.get('email')
        otp = str(randint(100000, 999999))
        body = f'Your email OTP is {otp}\n\nThis OTP will be expired in 10 minutes from now.'
        try:
            number_sent = send_mail(
                'OTP for User Registration',
                body,
                settings.EMAIL_HOST_USER,
                [email]
            )
            if number_sent < 1:
                return Response({"message": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            email_otp_obj, created = EmailOTP.objects.get_or_create(email=email)
            email_otp_obj.otp = otp
            email_otp_obj.save()
            return Response({"message": "Email OTP generated successfully"}, status=status.HTTP_200_OK)
        except:
            return Response({"message": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request):
        serializer = UserSerializer(request.user)
        return Response({'user': serializer.data}, status=status.HTTP_200_OK)