from django.urls import path, include
from rest_framework.routers import DefaultRouter
from utils.urls import RouterWithSingleView
from . import views

single_views = [
    {
        "route": "send-vertification-code/",
        "view": views.send_vertification_code,
        "name": "send-vertification-code",
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
        "route": "bio/",
        "view": views.bio,
        "name": "bio",
    },
    {
        "route": "info/",
        "view": views.info,
        "name": "info",
    },
]

router = RouterWithSingleView(single_views=single_views)


urlpatterns = [
    path("", include(router.urls)),
]
urlpatterns.extend(
    [path(route=i["route"], view=i["view"], name=i["name"]) for i in single_views]
)
