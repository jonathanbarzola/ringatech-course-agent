import unittest

from agent import TOOLS, parse_tool_arguments
from tools import Tools


class TestToolSchema(unittest.TestCase):
    def test_tool_descriptions_are_strings(self):
        for tool in TOOLS:
            with self.subTest(tool=tool["function"]["name"]):
                self.assertIsInstance(tool["function"]["description"], str)

    def test_parse_tool_arguments_accepts_json_string_and_dict(self):
        self.assertEqual(parse_tool_arguments('{"currency": "PEN"}'), {"currency": "PEN"})
        self.assertEqual(parse_tool_arguments({"currency": "PEN"}), {"currency": "PEN"})

    def test_tools_instance_accepts_currency_argument(self):
        tool = Tools()
        self.assertTrue(callable(tool.obtener_conversion))


if __name__ == "__main__":
    unittest.main()
