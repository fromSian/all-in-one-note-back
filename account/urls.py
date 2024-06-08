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
]

router = RouterWithSingleView(single_views=single_views)
router.register("test", views.UserViewSet, basename="test")


urlpatterns = [
    path("", include(router.urls)),
]
urlpatterns.extend(
    [path(route=i["route"], view=i["view"], name=i["name"]) for i in single_views]
)
