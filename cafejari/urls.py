from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication

from cafejari import views, settings
from cafejari.settings import DEBUG, LOCAL

schema_view = get_schema_view(
    info=openapi.Info(
      title="카페자리 API문서",
      default_version='v1',
      description="카페자리 서버의 API 문서입니다.",
    ),
    public=True,
    permission_classes=(AllowAny,),
    authentication_classes=(JWTAuthentication,)
)

urlpatterns = [
    path('', views.index),
    path('admin/', admin.site.urls),
    path('user/', include('user.urls')),
    path('cafe/', include('cafe.urls')),
    path('cafe_log/', include('cafe_log.urls')),
    path('leaderboard/', include('leaderboard.urls')),
    path('push/', include('notification.urls')),
    path('shop/', include('shop.urls')),
    path('request/', include('request.urls')),
]

if DEBUG:
    urlpatterns += [
       path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
       path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
       path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ]

if LOCAL:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
