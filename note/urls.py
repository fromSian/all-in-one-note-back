from django.urls import path, include
from utils.urls import RouterWithSingleView

from . import views

single_views = []

router = RouterWithSingleView(single_views=single_views)
router.register("test", views.NoteViewSet, basename="note")
router.register("item", views.NoteItemViewSet, basename="item")
urlpatterns = [path("", include(router.urls))]
urlpatterns.extend(
    [path(route=i["route"], view=i["view"], name=i["name"]) for i in single_views]
)
