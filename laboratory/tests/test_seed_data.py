from decimal import Decimal

from django.core.management import call_command
from django.test import TestCase

from laboratory.models import Result, Sample


class SeedDataCommandTests(TestCase):
    def test_seed_data_is_idempotent(self):
        call_command("seed_data")
        call_command("seed_data")

        sample = Sample.objects.get(sample_id="SMP-001")
        results = sample.results.order_by("parameter")

        self.assertEqual(Sample.objects.count(), 1)
        self.assertEqual(Result.objects.count(), 2)
        self.assertEqual(sample.status, Sample.Status.COMPLETED)
        self.assertQuerySetEqual(
            results,
            [
                ("Moisture", Decimal("8.75"), Result.Status.DRAFT),
                ("Protein", Decimal("12.5"), Result.Status.APPROVED),
            ],
            transform=lambda result: (result.parameter, result.value, result.status),
        )
