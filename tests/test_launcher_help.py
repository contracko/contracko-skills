from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class LauncherHelpTests(unittest.TestCase):
    def test_help_explains_products_without_dependencies_or_oauth(self):
        with tempfile.TemporaryDirectory() as directory:
            launcher = Path(directory) / "contracko-mcp.mjs"
            shutil.copyfile(ROOT / "packages/mcp/bin/contracko-mcp.js", launcher)
            for flag in ("--help", "-h"):
                with self.subTest(flag=flag):
                    result = subprocess.run(
                        ["node", str(launcher), flag],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stderr, "")
                    self.assertIn("CLM (clm_*)", result.stdout)
                    self.assertIn("without Parser credits", result.stdout)
                    self.assertIn("Contracko Parser (parser_*)", result.stdout)
                    self.assertIn("uses Parser credits", result.stdout)
                    self.assertIn("not needed to add contracts", result.stdout)
                    self.assertIn("CLM 7-day free trial", result.stdout)
                    self.assertIn("3 AI extractions, 10 Clara messages", result.stdout)
                    self.assertIn("subscribe to lift it; do not retry", result.stdout)
                    self.assertIn("Parser credits do not lift CLM trial limits", result.stdout)
                    self.assertIn("20 free credits once, not 20 extractions", result.stdout)
                    self.assertIn("a document costs 1-5", result.stdout)
                    self.assertIn("review doubles that", result.stdout)


if __name__ == "__main__":
    unittest.main()
