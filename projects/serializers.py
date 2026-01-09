from projects.models import Project
from rest_framework import serializers
from tasks.serializers import TaskSerializer


class ProjectSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)
    class Meta:
        model = Project
        fields = ["id", "name", "description", "tasks", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
