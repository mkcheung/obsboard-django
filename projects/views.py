from core.pagination import StandardResultsSetPagination
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from projects.serializers import (
    ProjectSerializer,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets, permissions
from projects.models import Project


class ProjectViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]

    search_fields = ["name", "description"]

    ordering_fields = [
        "created_at",
    ]
    ordering = ["-created_at"]

    def get_queryset(self):
        query_set = Project.objects.filter(user=self.request.user).order_by("-id")

        # handle search
        search_terms = self.request.query_params.get("search")
        if search_terms:
            query_set = query_set.filter(
                Q(name__icontains=search_terms) | Q(description__icontains=search_terms)
            )

        # handle sort and direction
        sort = self.request.query_params.get("sort")
        direction = self.request.query_params.get("dir")
        sortable_fields = {
            "created_at",
            "id",
        }
        if sort in sortable_fields:
            prefix = "-" if direction == "desc" else ""
            query_set.order_by(f"{prefix}{sort}")
        else:
            query_set.order_by("-created_at")

        return query_set

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
