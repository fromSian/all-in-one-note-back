from django.urls import path, include
from rest_framework.routers import DefaultRouter
from utils.urls import RouterWithSingleView
from . import views
from utils.google import GoogleLoginAccessView, GoogleLoginCallbackView
from utils.google_third import access_view, callback_view

single_views = [
    # {
    #     "route": "google/access/",
    #     "view": GoogleLoginAccessView.as_view(),
    #     "name": "google-access",
    # },
    {
        "route": "google/access/",
        "view": access_view,
        "name": "google-access",
    },
    {
        "route": "google/callback/",
        # "view": GoogleLoginCallbackView.as_view(),
        "view": callback_view,
        "name": "google-callback",
    },
    {
        "route": "send-code/",
        "view": views.send_code,
        "name": "send-code",
    },
    {
        "route": "verify-code/",
        "view": views.verify_code,
        "name": "verify-code",
    },
    {
        "route": "register/",
        "view": views.register,
        "name": "register",
    },
    {
        "route": "login/",
        "view": views.login,
        "name": "login",
    },
    {
        "route": "logout/",
        "view": views.logout,
        "name": "logout",
    },
    {
        "route": "password/",
        "view": views.PasswordView.as_view(),
        "name": "password",
    },
    {
        "route": "passwordnew/",
        "view": views.update_password,
        "name": "passwordnew",
    },
    {
        "route": "email/",
        "view": views.email,
        "name": "email",
    },
    {
        "route": "avatar/",
        "view": views.avatar,
        "name": "avatar",
    },
    {
        "route": "info/",
        "view": views.info,
        "name": "info",
    },
    {
        "route": "trial/",
        "view": views.trial,
        "name": "trial",
    },
    {
        "route": "trial-base/",
        "view": views.trial_to_base,
        "name": "trail_to_base",
    },
    {
        "route": "google-base/",
        "view": views.google_to_base,
        "name": "google_to_base",
    },
    {
        "route": "settings/",
        "view": views.SettingView.as_view(),
        "name": "settings",
    },
    {
        "route": "delete/",
        "view": views.delete_user,
        "name": "delete",
    },
    {
        "route": "clean_trial/",
        "view": views.clean_trial,
        "name": "clean_trial",
    },
]

router = RouterWithSingleView(single_views=single_views)
router.register("test", views.TestViewSet, basename="test")

urlpatterns = [
    path("", include(router.urls)),
]
urlpatterns.extend(
    [path(route=i["route"], view=i["view"], name=i["name"]) for i in single_views]
)
