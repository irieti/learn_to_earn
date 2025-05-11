from django.contrib import admin
from django.urls import path, include
from agent.views import FrontendView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("agent/", include("agent.urls")),
    path("", FrontendView.as_view(), name="frontend"),
    # API endpoints remain separate
    path("api/tasks/", include("agent.urls")),
]
