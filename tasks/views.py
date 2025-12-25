from core.pagination import StandardResultsSetPagination
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render
from tasks.serializers import (
    TaskSerializer,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets, permissions
from tasks.models import Task


class TaskViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter]

    filterset_fields = {
        "project_id": ["exact"],
        "status": ["exact"],
        "priority": ["exact"],
    }

    search_fields = ["title, description"]

    ordering_fields = [
        "created_at",
        "due_date",
        "priority",
        "status",
        "completed_at",
        "id",
    ]
    ordering = ["-created_at"]

    def get_queryset(self):
        query_set = Task.objects.filter(user=self.request.user)

        # get the search parameters
        project_id = self.request.query_params.get("project_id")
        status = self.request.query_params.get("status")
        priority = self.request.query_params.get("priority")

        # process the search parameters
        if project_id:
            query_set = query_set.filter(project_id=project_id)

        if status:
            query_set = query_set.filter(status=status)

        if priority:
            query_set = query_set.filter(priority=priority)

        # get the search terms
        searchterms = self.request.query_params.get("search")
        if searchterms:
            query_set = query_set.filter(
                Q(title__icontains=searchterms) | Q(description__icontains=searchterms)
            )

        # process the sort parameters
        sort = self.request.query_params.get("sort")
        direction = self.request.query_params.get("dir", "asc").lower()

        sortable_fields = {
            "created_at",
            "due_date",
            "priority",
            "status",
            "completed_at",
            "id",
        }

        if sort in sortable_fields:
            prefix = "-" if direction == "desc" else ""
            query_set = query_set.order_by(f"{prefix}{sort}")
        else:
            query_set = query_set.order_by("-created_at")

        return query_set

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
