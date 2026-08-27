import uuid
from enum import StrEnum

from django.db import models

type DjangoChoices = list[tuple[str, str]]


def django_choices(enum_type: type[StrEnum]) -> DjangoChoices:
    return [(member.value, member.name.replace("_", " ").capitalize()) for member in enum_type]


class SampleStatus(StrEnum):
    REGISTERED = "registered"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ResultStatus(StrEnum):
    DRAFT = "draft"
    APPROVED = "approved"


class Sample(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    sample_id = models.CharField(max_length=50, unique=True)
    order_id = models.CharField(max_length=50, db_index=True)
    client_id = models.CharField(max_length=50, db_index=True)
    status = models.CharField(
        max_length=20,
        choices=django_choices(SampleStatus),
        default=SampleStatus.REGISTERED,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sample_id"]

    def __str__(self) -> str:
        return self.sample_id


class Result(models.Model):
    result_id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    sample = models.ForeignKey(Sample, on_delete=models.PROTECT, related_name="results")
    parameter = models.CharField(max_length=255)
    value = models.DecimalField(max_digits=20, decimal_places=6)
    unit = models.CharField(max_length=50)
    status = models.CharField(
        max_length=20,
        choices=django_choices(ResultStatus),
        default=ResultStatus.DRAFT,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at", "result_id"]
        constraints = [
            models.UniqueConstraint(
                fields=["sample", "parameter"],
                name="unique_result_parameter_per_sample",
            )
        ]

    def __str__(self) -> str:
        return f"{self.sample.sample_id}: {self.parameter}"
