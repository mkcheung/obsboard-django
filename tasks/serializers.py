from projects.models import Project
from tasks.models import Task
from rest_framework import serializers


class TaskSerializer(serializers.ModelSerializer):
    project_id = serializers.PrimaryKeyRelatedField(
        source="project",
        queryset=Project.objects.all(),
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "project_id",
            "title",
            "description",
            "status",
            "priority",
            "due_date",
            "estimate_minutes",
            "completed_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
