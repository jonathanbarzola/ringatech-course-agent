import unittest

from agent import TOOLS


class TestToolSchema(unittest.TestCase):
    def test_tool_descriptions_are_strings(self):
        for tool in TOOLS:
            with self.subTest(tool=tool["function"]["name"]):
                self.assertIsInstance(tool["function"]["description"], str)


if __name__ == "__main__":
    unittest.main()
