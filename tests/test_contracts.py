"""Exercise the documentation checker through its CLI, including negative drift cases."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ContractDocumentationTests(unittest.TestCase):
    def check(self, text):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "skills").mkdir()
            (root / "skills/example.md").write_text(text)
            return subprocess.run(
                ["python3", str(ROOT / "scripts/check_contracts.py"), "--root", str(root)],
                capture_output=True, text=True,
            )

    def call(self, args, tool="clm_list_contracts"):
        return f"```json mcp:{tool}\n{json.dumps(args)}\n```\n"

    def test_renewal_and_vendor_examples(self):
        examples = self.call({"endDateFrom": "2026-09-01", "endDateTo": "2026-11-30"})
        examples += self.call({"query": "Acme", "type": "company"}, "clm_list_parties")
        examples += self.call({"counterpartyId": "b563cddb-121f-4f7b-9c43-687a524ccbe2"})
        result = self.check(examples)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_folder_filing_and_access_examples(self):
        contract = "b563cddb-121f-4f7b-9c43-687a524ccbe2"
        examples = self.call({"folderId": contract, "query": "Acme"})
        examples += self.call({"parentFolderId": None, "limit": 50}, "clm_list_folders")
        examples += self.call({"name": "Suppliers", "parentFolderId": None}, "clm_create_folder")
        examples += self.call({"id": contract, "folderId": None}, "clm_move_contract")
        examples += self.call({"id": contract}, "clm_get_contract_access")
        examples += self.call({"id": contract}, "clm_get_folder")
        examples += self.call({"id": contract}, "clm_get_folder_access")
        examples += self.call({"id": contract, "name": "Vendors"}, "clm_rename_folder")
        examples += self.call({"id": contract, "parentFolderId": None}, "clm_move_folder")
        result = self.check(examples)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_invalid_folder_arguments(self):
        contract = "b563cddb-121f-4f7b-9c43-687a524ccbe2"
        for tool, args in (
            ("clm_list_contracts", {"folderId": None}),
            ("clm_list_folders", {"cursor": "invented"}),
            ("clm_list_folders", {"parentFolderId": "hidden-folder"}),
            ("clm_move_contract", {"id": contract}),
            ("clm_move_contract", {"id": contract, "folderId": 123}),
            ("clm_get_folder_access", {"id": contract, "permission": "admin"}),
        ):
            with self.subTest(tool=tool, args=args):
                self.assertNotEqual(self.check(self.call(args, tool)).returncode, 0)

    def test_rejects_obsolete_folder_claims(self):
        for claim in ("folderId` you can read and cannot set", "Creating folders and moving contracts is app work"):
            with self.subTest(claim=claim):
                self.assertNotEqual(self.check(self.call({}) + claim).returncode, 0)

    def test_rejects_invented_argument_and_tool(self):
        for text in (self.call({"minimumAnnualValue": 25000}), self.call({}) + "Use `clm_magic_search`."):
            with self.subTest(text=text):
                self.assertNotEqual(self.check(text).returncode, 0)

    def test_rejects_invalid_windows_and_list_inputs(self):
        for args in (
            {"noticeDateFrom": "2026-02-30"},
            {"endDateFrom": "2026-12-01", "endDateTo": "2026-09-01"},
            {"status": "draft"}, {"limit": 101}, {"limit": 1.5}, {"limit": True},
            {"query": ""}, {"counterpartyId": "Acme"},
        ):
            with self.subTest(args=args):
                self.assertNotEqual(self.check(self.call(args)).returncode, 0)

    def test_rejects_obsolete_rollback_and_filter_claims(self):
        for claim in ("Metadata filters still do not exist", "the outcome is that nothing was written"):
            with self.subTest(claim=claim):
                self.assertNotEqual(self.check(self.call({}) + claim).returncode, 0)

    def test_requires_checked_examples(self):
        self.assertNotEqual(self.check("No examples.").returncode, 0)

    def test_committed_skills_match_released_catalog(self):
        result = subprocess.run(["python3", str(ROOT / "scripts/check_contracts.py")], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
