from decimal import Decimal

import factory

from laboratory.models import Result, Sample


class SampleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Sample
        django_get_or_create = ("sample_id",)

    sample_id = factory.Sequence(lambda number: f"SMP-{number:03d}")
    order_id = factory.Sequence(lambda number: f"ORD-2026-{number:03d}")
    client_id = factory.Sequence(lambda number: f"CLIENT-{number:03d}")
    status = Sample.Status.REGISTERED


class ResultFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Result
        django_get_or_create = ("sample", "parameter")

    sample = factory.SubFactory(SampleFactory)
    parameter = factory.Sequence(lambda number: f"Parameter {number}")
    value = Decimal("1.0")
    unit = "%"
    status = Result.Status.DRAFT
