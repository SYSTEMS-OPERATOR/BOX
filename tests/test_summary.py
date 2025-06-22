import unittest
from pathlib import Path

from scripts.summary import load_json, list_styles, summary_key, summary_server


class TestSummary(unittest.TestCase):
    def test_load_server(self):
        data = load_json(Path('CFG') / 'SERVER.json')
        self.assertIn('PROJECT_NAME', data)

    def test_list_styles(self):
        styles = list_styles()
        self.assertGreater(len(styles), 0)
        self.assertIn('anthemic', styles)

    def test_summary_key(self):
        summary = summary_key()
        self.assertIn('Monday', summary)
        self.assertIn('Cynical', summary)

    def test_summary_server(self):
        summary = summary_server()
        self.assertIn('SOPHY', summary)


if __name__ == '__main__':
    unittest.main()
