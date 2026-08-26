from decimal import Decimal

from django.core.management.base import BaseCommand

from laboratory.factories import ResultFactory, SampleFactory
from laboratory.models import Result, Sample


class Command(BaseCommand):
    help = "Create idempotent sample laboratory data"

    def handle(self, *args, **options):
        sample = SampleFactory.create(
            sample_id="SMP-001",
            order_id="ORD-2026-001",
            client_id="CLIENT-001",
            status=Sample.Status.COMPLETED,
        )
        ResultFactory.create(
            sample=sample,
            parameter="Protein",
            value=Decimal("12.5"),
            unit="%",
            status=Result.Status.APPROVED,
        )
        ResultFactory.create(
            sample=sample,
            parameter="Moisture",
            value=Decimal("8.75"),
            unit="%",
            status=Result.Status.DRAFT,
        )
        self.stdout.write(self.style.SUCCESS("Seed data is ready."))
