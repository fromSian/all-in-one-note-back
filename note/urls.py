from django.urls import path, include
from utils.urls import RouterWithSingleView

from . import views

single_views = [
    {
        "route": "markdown/",
        "view": views.note_content_md,
        "name": "markdown",
    }
]

router = RouterWithSingleView(single_views=single_views)
router.register("navigation", views.NoteViewSet, basename="navigation")
router.register("content", views.NoteItemViewSet, basename="content")
urlpatterns = [path("", include(router.urls))]
urlpatterns.extend(
    [path(route=i["route"], view=i["view"], name=i["name"]) for i in single_views]
)
