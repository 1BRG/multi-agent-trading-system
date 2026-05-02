from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from accounts.views import (
    CurrentUserView,
    LoginView,
    PasswordChangeView,
    RegisterView,
    SocialAuthCallbackView,
    SocialAuthStartView,
    UserAdminViewSet,
    UserMeView,
)
from backtests.views import BacktestRunViewSet
from conversations.views import (
    ChatMessageViewSet,
    ChatThreadViewSet,
    DebateMessageViewSet,
    DebateSessionViewSet,
)
from market.views import AssetListAPIView, AssetPricesAPIView, AssetPriceViewSet, AssetViewSet
from strategies.views import StrategyViewSet

router = DefaultRouter(trailing_slash=False)
router.register("assets", AssetViewSet, basename="asset")
router.register("asset-prices", AssetPriceViewSet, basename="asset-price")
router.register("strategies", StrategyViewSet, basename="strategy")
router.register("backtests", BacktestRunViewSet, basename="backtest")
router.register("chats", ChatThreadViewSet, basename="chat")
router.register("chat-messages", ChatMessageViewSet, basename="chat-message")
router.register("debates", DebateSessionViewSet, basename="debate")
router.register("debate-messages", DebateMessageViewSet, basename="debate-message")
router.register("users", UserAdminViewSet, basename="user-admin")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/register", RegisterView.as_view(), name="auth-register"),
    path("auth/login", LoginView.as_view(), name="auth-login"),
    path("auth/social/<str:provider>/start", SocialAuthStartView.as_view(), name="auth-social-start"),
    path("auth/social/<str:provider>/callback", SocialAuthCallbackView.as_view(), name="auth-social-callback"),
    path("auth/me", CurrentUserView.as_view(), name="auth-me"),
    path("users/me", UserMeView.as_view(), name="users-me"),
    path("users/me/password", PasswordChangeView.as_view(), name="users-me-password"),
    path("api/assets", AssetListAPIView.as_view(), name="api-assets"),
    path("api/assets/<str:symbol>/prices", AssetPricesAPIView.as_view(), name="api-asset-prices"),
    path("", include(router.urls)),
    path("health", lambda request: JsonResponse({"status": "ok"})),
]

if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
