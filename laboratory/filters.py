import django_filters

from laboratory.models import Result, Sample


class SampleFilter(django_filters.FilterSet):
    class Meta:
        model = Sample
        fields = ["status", "order_id", "client_id"]


class ResultFilter(django_filters.FilterSet):
    sample_id = django_filters.UUIDFilter(field_name="sample_id")

    class Meta:
        model = Result
        fields = ["status", "sample_id", "parameter"]
