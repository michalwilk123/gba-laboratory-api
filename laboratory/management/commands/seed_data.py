from decimal import Decimal
from typing import override

from django.core.management.base import BaseCommand

from laboratory.factories import ResultFactory, SampleFactory
from laboratory.models import ResultStatus, SampleStatus


class Command(BaseCommand):
    help = "Create idempotent sample laboratory data"

    @override
    def handle(self, *args: object, **options: object) -> None:
        sample = SampleFactory.create(
            sample_id="SMP-001",
            order_id="ORD-2026-001",
            client_id="CLIENT-001",
            status=SampleStatus.COMPLETED,
        )
        ResultFactory.create(
            sample=sample,
            parameter="Protein",
            value=Decimal("12.5"),
            unit="%",
            status=ResultStatus.APPROVED,
        )
        ResultFactory.create(
            sample=sample,
            parameter="Moisture",
            value=Decimal("8.75"),
            unit="%",
            status=ResultStatus.DRAFT,
        )
        self.stdout.write(self.style.SUCCESS("Seed data is ready."))
