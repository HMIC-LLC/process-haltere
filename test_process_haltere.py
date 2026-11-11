import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parent / "process_haltere.py"
SPEC = importlib.util.spec_from_file_location("process_haltere", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class ProcessHaltereTests(unittest.TestCase):
    def test_thresholds_are_strict(self):
        self.assertEqual(MODULE.evaluate(11, 180, 240, 240)["classification"], "NOMINAL")
        self.assertEqual(MODULE.evaluate(11, 180, 240, 241)["classification"], "HALTERE_WARNING")
        self.assertEqual(MODULE.evaluate(11, 180, 240, 480)["classification"], "HALTERE_WARNING")
        self.assertEqual(MODULE.evaluate(11, 180, 240, 481)["classification"], "HALTERE_RED_FLAG")

    def test_invalid_inputs_are_rejected(self):
        for args in ((-1, 180, 240, 0), (1, 0, 240, 0), (1, 240, 180, 0), (1, 180, 240, -1)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                MODULE.evaluate(*args)

    def test_operator_example_is_red_flag(self):
        result = MODULE.evaluate(11, 180, 240, 11 * 3600)
        self.assertEqual(result["classification"], "HALTERE_RED_FLAG")
        self.assertEqual(result["expected_remaining_seconds"]["high"], 2640)
        self.assertEqual(result["remaining_envelope_ratio"], 15.0)

    def test_nominal_progress(self):
        result = MODULE.evaluate(11, 180, 240, 180)
        self.assertEqual(result["classification"], "NOMINAL")

    def test_warning_after_one_upper_unit(self):
        result = MODULE.evaluate(11, 180, 240, 300)
        self.assertEqual(result["classification"], "HALTERE_WARNING")

    def test_complete(self):
        result = MODULE.evaluate(0, 180, 240, 0)
        self.assertEqual(result["classification"], "COMPLETE")

    def test_blockheight_is_provenance_only(self):
        result = MODULE.evaluate(2, 180, 240, 60, start_block=100, current_block=103)
        self.assertEqual(result["block_delta"], 3)
        self.assertEqual(result["blockheight_policy"], "provenance_only_never_elapsed_or_eta")
        self.assertNotIn("block_elapsed_estimate_seconds", result)


if __name__ == "__main__":
    unittest.main()
