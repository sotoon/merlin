from django.urls import re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions


def get_doc_urls():
    schema_view = get_schema_view(
        openapi.Info(
            title="Merlin Backend API",
            default_version="v1",
            description="Merlin API Spec",
            terms_of_service="https://github.com/sotoon/merlin/blob/main/LICENSE",
            contact=openapi.Contact(email="contact@sotoon.ir"),
            license=openapi.License(name="BSD 3-Clause License"),
        ),
        public=True,
        permission_classes=[permissions.AllowAny],
    )

    urls = [
        re_path(
            r"^api/swagger(?P<format>\.json|\.yaml)$",
            schema_view.without_ui(cache_timeout=0),
            name="schema-json",
        ),
        re_path(
            r"^api/swagger/$",
            schema_view.with_ui("swagger", cache_timeout=0),
            name="schema-swagger-ui",
        ),
        re_path(
            r"^api/redoc/$",
            schema_view.with_ui("redoc", cache_timeout=0),
            name="schema-redoc",
        ),
    ]

    return urls
