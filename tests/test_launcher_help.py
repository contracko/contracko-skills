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


if __name__ == "__main__":
    unittest.main()
