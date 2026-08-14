import unittest
from pathlib import Path

from kartini_agent_kit.commit_message import conventional_message
from kartini_agent_kit.config import missing_keys, parse_env_file
from kartini_agent_kit.review import has_blocking_findings, review_diff
from kartini_agent_kit.ticket import extract_ticket


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


if __name__ == "__main__":
    unittest.main()
