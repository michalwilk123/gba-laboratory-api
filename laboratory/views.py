import logging
from typing import Final

from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from laboratory.filters import ResultFilter, SampleFilter
from laboratory.models import Result, ResultStatus, Sample
from laboratory.serializers import (
    ResultSerializer,
    SampleExportSerializer,
    SampleSerializer,
    SampleStatusSerializer,
)

logger: Final[logging.Logger] = logging.getLogger(__name__)


class SampleViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Sample.objects.all()
    serializer_class = SampleSerializer
    filterset_class = SampleFilter
    lookup_field = "sample_id"

    @extend_schema(request=SampleStatusSerializer, responses=SampleSerializer)
    @action(detail=True, methods=["patch"])
    def status(self, request: Request, *args: object, **kwargs: object) -> Response:
        sample = self.get_object()
        serializer = SampleStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sample.status = serializer.validated_data["status"]
        sample.save(update_fields=["status", "updated_at"])
        logger.info(
            "sample_status_updated",
            extra={
                "sample_id": sample.sample_id,
                "sample_uuid": str(sample.id),
                "sample_status": sample.status,
            },
        )
        return Response(SampleSerializer(sample).data)

    @extend_schema(responses=ResultSerializer(many=True))
    @action(detail=True, methods=["get"])
    def results(self, request: Request, *args: object, **kwargs: object) -> Response:
        sample = self.get_object()
        queryset = sample.results.all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(ResultSerializer(page, many=True).data)
        return Response(ResultSerializer(queryset, many=True).data)


class ResultViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Result.objects.select_related("sample")
    serializer_class = ResultSerializer
    filterset_class = ResultFilter
    lookup_field = "result_id"

    @extend_schema(request=None, responses=ResultSerializer)
    @action(detail=True, methods=["patch"])
    def approve(self, request: Request, *args: object, **kwargs: object) -> Response:
        result = self.get_object()
        if result.status != ResultStatus.APPROVED:
            result.status = ResultStatus.APPROVED
            result.save(update_fields=["status", "updated_at"])
            logger.info(
                "result_approved",
                extra={
                    "result_id": str(result.result_id),
                    "sample_id": result.sample.sample_id,
                },
            )
        return Response(ResultSerializer(result).data)


class IntegrationExportView(GenericAPIView):
    serializer_class = SampleExportSerializer

    @extend_schema(responses=SampleExportSerializer)
    def get(self, request: Request, sample_id: str) -> Response:
        approved_results = Result.objects.filter(status=ResultStatus.APPROVED)
        queryset = Sample.objects.prefetch_related(
            Prefetch("results", queryset=approved_results, to_attr="approved_results")
        )
        sample = get_object_or_404(queryset, sample_id=sample_id)
        serializer = self.get_serializer(sample)
        return Response(serializer.data, status=status.HTTP_200_OK)
