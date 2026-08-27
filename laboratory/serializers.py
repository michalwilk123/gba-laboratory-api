from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from laboratory.models import Result, ResultStatus, Sample, SampleStatus, django_choices


class SampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sample
        fields = [
            "sample_id",
            "order_id",
            "client_id",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class SampleStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=django_choices(SampleStatus))


class ResultSerializer(serializers.ModelSerializer):
    sample_id = serializers.SlugRelatedField(
        queryset=Sample.objects.all(),
        slug_field="sample_id",
        source="sample",
    )
    status = serializers.ChoiceField(
        choices=django_choices(ResultStatus), default=ResultStatus.DRAFT
    )

    class Meta:
        model = Result
        fields = [
            "result_id",
            "sample_id",
            "parameter",
            "value",
            "unit",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["result_id", "created_at", "updated_at"]
        validators = [
            UniqueTogetherValidator(
                queryset=Result.objects.all(),
                fields=["sample_id", "parameter"],
                message="A result for this sample and parameter already exists.",
            )
        ]

    def validate_status(self, value: str) -> str:
        if value != ResultStatus.DRAFT:
            raise serializers.ValidationError("New results must be created as draft.")
        return value


class ExportResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ["parameter", "value", "unit", "status"]


class SampleExportSerializer(serializers.ModelSerializer):
    sample_status = serializers.CharField(source="status")
    results = ExportResultSerializer(source="approved_results", many=True)

    class Meta:
        model = Sample
        fields = ["sample_id", "order_id", "client_id", "sample_status", "results"]
