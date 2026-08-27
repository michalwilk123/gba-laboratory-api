import uuid

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from laboratory.factories import ResultFactory, SampleFactory
from laboratory.models import ResultStatus, SampleStatus


class AuthenticatedAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="api-user",
            password="test-password-123",
        )

    def setUp(self):
        access_token = RefreshToken.for_user(self.user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")


class AuthenticationTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="api-user",
            password="test-password-123",
        )

    def test_business_endpoint_requires_authentication(self):
        response = self.client.get(reverse("sample-list"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_username_and_password_return_jwt_pair(self):
        response = self.client.post(
            reverse("token-obtain-pair"),
            {"username": self.user.username, "password": "test-password-123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_api_documentation_is_public(self):
        response = self.client.get(reverse("schema"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SampleApiTests(AuthenticatedAPITestCase):
    def test_trailing_slash_route_is_not_exposed(self):
        response = self.client.get("/samples/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_list_and_retrieve_sample(self):
        payload = {
            "sample_id": "SMP-001",
            "order_id": "ORD-2026-001",
            "client_id": "CLIENT-001",
            "status": "registered",
        }

        create_response = self.client.post(reverse("sample-list"), payload, format="json")
        list_response = self.client.get(reverse("sample-list"))
        detail_response = self.client.get(
            reverse("sample-detail", kwargs={"sample_id": payload["sample_id"]})
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("id", create_response.data)
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data["count"], 1)
        self.assertEqual(detail_response.data["sample_id"], payload["sample_id"])

    def test_sample_id_must_be_unique(self):
        SampleFactory.create(
            sample_id="SMP-001",
            order_id="ORD-2026-001",
            client_id="CLIENT-001",
        )
        payload = {
            "sample_id": "SMP-001",
            "order_id": "ORD-2026-002",
            "client_id": "CLIENT-002",
        }

        response = self.client.post(reverse("sample-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("sample_id", response.data)

    def test_status_action_accepts_any_allowed_status(self):
        sample = SampleFactory.create()

        response = self.client.patch(
            reverse("sample-status", kwargs={"sample_id": sample.sample_id}),
            {"status": "completed"},
            format="json",
        )

        sample.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(sample.status, SampleStatus.COMPLETED)

    def test_arbitrary_sample_update_is_not_exposed(self):
        sample = SampleFactory.create()

        response = self.client.patch(
            reverse("sample-detail", kwargs={"sample_id": sample.sample_id}),
            {"client_id": "CLIENT-002"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_invalid_status_returns_field_error(self):
        sample = SampleFactory.create()

        response = self.client.patch(
            reverse("sample-status", kwargs={"sample_id": sample.sample_id}),
            {"status": "unknown"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("status", response.data)

    def test_samples_can_be_filtered(self):
        SampleFactory.create(
            sample_id="SMP-001",
            order_id="ORD-2026-001",
            client_id="CLIENT-001",
            status=SampleStatus.REGISTERED,
        )
        SampleFactory.create(
            sample_id="SMP-002",
            order_id="ORD-2026-002",
            client_id="CLIENT-002",
            status=SampleStatus.COMPLETED,
        )

        response = self.client.get(reverse("sample-list"), {"status": "completed"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["sample_id"], "SMP-002")


class ResultApiTests(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()
        self.sample = SampleFactory.create()

    def test_create_and_list_result_for_sample(self):
        payload = {
            "sample_id": self.sample.sample_id,
            "parameter": "Protein",
            "value": 12.5,
            "unit": "%",
            "status": "draft",
        }

        create_response = self.client.post(reverse("result-list"), payload, format="json")
        sample_results_response = self.client.get(
            reverse("sample-results", kwargs={"sample_id": self.sample.sample_id})
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(uuid.UUID(create_response.data["result_id"]).version, 7)
        self.assertEqual(create_response.data["sample_id"], self.sample.sample_id)
        self.assertEqual(sample_results_response.status_code, status.HTTP_200_OK)
        self.assertEqual(sample_results_response.data["count"], 1)
        self.assertEqual(sample_results_response.data["results"][0]["parameter"], "Protein")

    def test_result_for_unknown_sample_is_rejected(self):
        payload = {
            "sample_id": "SMP-404",
            "parameter": "Protein",
            "value": 12.5,
            "unit": "%",
        }

        response = self.client.post(reverse("result-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("sample_id", response.data)

    def test_result_parameter_must_be_unique_per_sample(self):
        ResultFactory.create(
            sample=self.sample,
            parameter="Protein",
        )
        payload = {
            "sample_id": self.sample.sample_id,
            "parameter": "Protein",
            "value": 13,
            "unit": "%",
        }

        response = self.client.post(reverse("result-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_new_result_cannot_be_created_as_approved(self):
        payload = {
            "sample_id": self.sample.sample_id,
            "parameter": "Protein",
            "value": 12.5,
            "unit": "%",
            "status": "approved",
        }

        response = self.client.post(reverse("result-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("status", response.data)

    def test_approval_is_one_way_and_idempotent(self):
        result = ResultFactory.create(
            sample=self.sample,
            parameter="Protein",
        )
        url = reverse("result-approve", kwargs={"result_id": result.result_id})

        first_response = self.client.patch(url, {}, format="json")
        second_response = self.client.patch(url, {}, format="json")

        result.refresh_from_db()
        self.assertEqual(first_response.status_code, status.HTTP_200_OK)
        self.assertEqual(second_response.status_code, status.HTTP_200_OK)
        self.assertEqual(result.status, ResultStatus.APPROVED)

    def test_results_can_be_filtered_by_business_sample_id(self):
        ResultFactory.create(sample=self.sample, parameter="Protein")
        ResultFactory.create(parameter="Moisture")

        response = self.client.get(reverse("result-list"), {"sample_id": self.sample.sample_id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["sample_id"], self.sample.sample_id)
        self.assertEqual(response.data["results"][0]["parameter"], "Protein")


class IntegrationExportTests(AuthenticatedAPITestCase):
    def test_export_contains_only_approved_results(self):
        sample = SampleFactory.create(status=SampleStatus.COMPLETED)
        ResultFactory.create(
            sample=sample,
            parameter="Protein",
            status=ResultStatus.APPROVED,
        )
        ResultFactory.create(
            sample=sample,
            parameter="Moisture",
            status=ResultStatus.DRAFT,
        )

        response = self.client.get(
            reverse("integration-export", kwargs={"sample_id": sample.sample_id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("id", response.data)
        self.assertEqual(response.data["sample_id"], sample.sample_id)
        self.assertEqual(response.data["sample_status"], "completed")
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["parameter"], "Protein")

    def test_export_for_unknown_sample_returns_not_found(self):
        response = self.client.get(reverse("integration-export", kwargs={"sample_id": "SMP-404"}))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
