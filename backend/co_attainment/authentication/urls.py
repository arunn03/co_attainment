from django.urls import path, include
from .views import *

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name = 'authentication'

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='get_token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='refresh_token'),
    path('email-otp/', EmailOTPGenerationAPIView.as_view(), name='email-otp'),
    path('user/', UserAPIView.as_view(), name='user-data'),
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
]
