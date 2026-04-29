from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from accounts.views import (
    CurrentUserView,
    LoginView,
    PasswordChangeView,
    RegisterView,
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
from market.views import StockPriceViewSet, StockViewSet
from strategies.views import StrategyViewSet

router = DefaultRouter(trailing_slash=False)
router.register("stocks", StockViewSet, basename="stock")
router.register("stock-prices", StockPriceViewSet, basename="stock-price")
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
    path("auth/me", CurrentUserView.as_view(), name="auth-me"),
    path("users/me", UserMeView.as_view(), name="users-me"),
    path("users/me/password", PasswordChangeView.as_view(), name="users-me-password"),
    path("", include(router.urls)),
    path("health", lambda request: JsonResponse({"status": "ok"})),
]
