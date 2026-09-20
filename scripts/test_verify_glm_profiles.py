"""Run with python -m unittest discover -s scripts -p test_verify_glm_profiles.py."""
import unittest

from verify_glm_profiles import self_test


class VerifierRegressionTests(unittest.TestCase):
    def test_real_git_export_apply_and_reject_tampering(self):
        # Includes updated-hash patch tampering, not just checksum rejection.
        self_test()


if __name__ == "__main__":
    unittest.main()
