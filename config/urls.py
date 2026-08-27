from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.permissions import AllowAny
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from laboratory.views import IntegrationExportView, ResultViewSet, SampleViewSet

router = SimpleRouter(trailing_slash=False)
router.register("samples", SampleViewSet)
router.register("results", ResultViewSet)

urlpatterns = [
    *router.urls,
    path(
        "integration/export/<str:sample_id>",
        IntegrationExportView.as_view(),
        name="integration-export",
    ),
    path(
        "auth/token",
        TokenObtainPairView.as_view(permission_classes=[AllowAny]),
        name="token-obtain-pair",
    ),
    path(
        "auth/token/refresh",
        TokenRefreshView.as_view(permission_classes=[AllowAny]),
        name="token-refresh",
    ),
    path("schema", SpectacularAPIView.as_view(permission_classes=[AllowAny]), name="schema"),
    path(
        "docs",
        SpectacularSwaggerView.as_view(url_name="schema", permission_classes=[AllowAny]),
        name="swagger-ui",
    ),
    path(
        "redoc",
        SpectacularRedocView.as_view(url_name="schema", permission_classes=[AllowAny]),
        name="redoc",
    ),
]
