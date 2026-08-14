import unittest
from unittest.mock import patch
from pathlib import Path

from kartini_agent_kit.commit_message import conventional_message
from kartini_agent_kit.config import missing_keys, parse_env_file
from kartini_agent_kit.review import has_blocking_findings, review_diff
from kartini_agent_kit.ticket import extract_ticket
from kartini_agent_kit.validation import detect_validations


class CoreTests(unittest.TestCase):
    def test_extract_ticket_from_branch(self):
        self.assertEqual(extract_ticket("feature/KAIRA-654-payment"), "KAIRA-654")
        self.assertIsNone(extract_ticket("main"))


    def test_commit_message_is_conventional(self):
        self.assertEqual(conventional_message("KAIRA-654", "Add Payment Validation"), "feat(KAIRA-654): add payment validation")
        self.assertEqual(conventional_message("KAIRA-654", "Fix payment bug"), "fix(KAIRA-654): fix payment bug")


    def test_only_blocking_findings_stop(self):
        findings = review_diff("+password = 'a-long-secret-value'\n")
        self.assertTrue(has_blocking_findings(findings))
        self.assertFalse(has_blocking_findings([]))


    def test_env_parser_and_missing_keys(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as directory:
            env = Path(directory) / ".env"
            env.write_text("# comment\nJIRA_URL='https://example.atlassian.net'\n", encoding="utf-8")
            values = parse_env_file(env)
            self.assertEqual(values["JIRA_URL"], "https://example.atlassian.net")
            self.assertIn("JIRA_EMAIL", missing_keys(values))

    def test_validation_detects_multiple_project_checks(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "package.json").write_text(
                '{"scripts":{"lint":"eslint .","typecheck":"tsc --noEmit","test":"jest","build":"vite build"}}',
                encoding="utf-8",
            )
            commands = detect_validations(root)
            self.assertEqual(commands, [
                ["npm", "run", "lint"],
                ["npm", "run", "typecheck"],
                ["npm", "run", "test"],
                ["npm", "run", "build"],
            ])

    @patch("kartini_agent_kit.integrations.subprocess.run")
    def test_bitbucket_remote_parser(self, run):
        from kartini_agent_kit.integrations import bitbucket_remote
        run.return_value.returncode = 0
        run.return_value.stdout = "git@bitbucket.org:team/payments.git\n"
        self.assertEqual(bitbucket_remote(Path(".")), ("team", "payments"))

    @patch("kartini_agent_kit.git_inspection.subprocess.run")
    def test_untracked_file_is_included_in_review_diff(self, run):
        from tempfile import TemporaryDirectory
        from kartini_agent_kit.git_inspection import inspect_repository
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "new.py").write_text("password = 'secret-value'\n", encoding="utf-8")

            def fake_run(command, **kwargs):
                class Result:
                    returncode = 0
                    stderr = ""
                    stdout = ""
                result = Result()
                if command[1:4] == ["rev-parse", "--show-toplevel"]:
                    result.stdout = str(root) + "\n"
                elif command[1:3] == ["branch", "--show-current"]:
                    result.stdout = "feature/KAIRA-1-test\n"
                elif command[1:3] == ["status", "--short"]:
                    result.stdout = "?? new.py\n"
                elif command[1:4] == ["ls-files", "--others", "--exclude-standard"]:
                    result.stdout = "new.py\n"
                elif command[1:3] == ["diff", "--no-index"]:
                    result.stdout = "+password = 'secret-value'\n"
                run.return_value = result
                return result

            run.side_effect = fake_run
            state = inspect_repository(root)
            self.assertIn("new.py", state.changed_files)
            self.assertIn("secret-value", state.diff)


if __name__ == "__main__":
    unittest.main()
