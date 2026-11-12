"""Tests for person and mail service boundaries.

These tests deliberately use Flask request contexts and mocked persistence so
they can run without Firebase credentials or a MySQL database.
"""

import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from flask import Flask

from backend.modules.person.models.mail_model import Mail
from backend.modules.person.services import mail_services, person_services


class MailModelTests(unittest.TestCase):
    def test_from_json_parses_iso8601_timestamps(self):
        mail = Mail.from_json(
            {
                "uid": "3577",
                "person_uid_fk": "12370",
                "email": "person@example.com",
                "created_at": "2024-06-02T17:33:48.000Z",
                "updated_at": "2026-02-20T08:28:30.000Z",
            }
        )

        self.assertEqual(
            mail.created_at,
            datetime(2024, 6, 2, 17, 33, 48, tzinfo=timezone.utc),
        )
        self.assertEqual(
            mail.updated_at,
            datetime(2026, 2, 20, 8, 28, 30, tzinfo=timezone.utc),
        )


class MailServiceTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)

    def test_upsert_mail_returns_missing_fields_without_commit(self):
        with self.app.test_request_context():
            with patch.object(mail_services, "json_response") as response:
                mail_services.upsert_mail(
                    data={"email": ""},
                    person_uid_fk=12370,
                )

        response.assert_called_once_with(response=mail_services.ApiResponse.MISSING_FIELDS)


class PersonServiceIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)

    def test_upsert_person_with_empty_organization_returns_missing_fields(self):
        with self.app.test_request_context(
            "/person/ui",
            method="POST",
            json={"uid": "12370", "main_organization_uid_fk": ""},
        ):
            with patch.object(person_services, "json_response") as response:
                person_services.person_upsert()

        response.assert_called_once_with(response="MISSING_FIELDS")

    def test_existing_person_is_updated_without_inserting_new_parent(self):
        person_data = SimpleNamespace(
            uid=12370,
            main_organization_uid_fk=20,
            name="Updated Person",
            id_number="825.664.293-91",
            person_type=1,
            is_active=2,
            is_supplier=0,
            iso2alpha="BR",
            mails=[],
            phones=[],
            addresses=[],
            br_tax_regimes=[],
            activities=[],
            partners=[],
            financial=None,
            natural=None,
            supplementary=None,
            legal=None,
        )
        selected = SimpleNamespace(uid=12370)
        session = MagicMock()
        session.get.return_value = selected
        database = SimpleNamespace(session=session)

        with self.app.test_request_context(
            "/person/ui",
            method="POST",
            json={"uid": "12370", "main_organization_uid_fk": 20},
        ):
            with patch.object(person_services.Person, "from_json", return_value=person_data), patch.object(
                person_services, "db", database
            ), patch.object(person_services, "json_response"):
                person_services.person_upsert()

        session.get.assert_called_once_with(person_services.Person, 12370)
        session.commit.assert_called_once_with()
        session.add.assert_called_once_with(selected)


if __name__ == "__main__":
    unittest.main()
