from allauth.account.views import LoginView
from django.urls import path, include

from rest_framework import routers

from cafejari.settings import DEBUG
from user import views
from user.views import UserViewSet, ProfileViewSet, CustomTokenRefreshView

router = routers.DefaultRouter()
router.register('', UserViewSet)
router.register('profile', ProfileViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('kakao/login/', views.kakao_login),
    path('kakao/login/callback/', views.kakao_login_callback),
    path('kakao/login/finish/', views.KakaoLogin.as_view(), name='kakao_login_todjango'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh')
]

if DEBUG:
    urlpatterns += path("login/", LoginView.as_view(), name="account_login")
