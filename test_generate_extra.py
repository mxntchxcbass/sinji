import json
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent

class QuestionBankGenerationTest(unittest.TestCase):
    def test_seeded_generation_covers_five_areas_with_valid_keys(self):
        with tempfile.TemporaryDirectory() as td:
            out = pathlib.Path(td) / 'bank.json'
            subprocess.run(['node', str(ROOT / 'generate_question_bank.js'), '--seed', '456', '--count', '3', '--output', str(out)], check=True)
            bank = json.loads(out.read_text(encoding='utf-8'))
        items = list(bank['q'].values())
        self.assertEqual(len(items), 15)
        self.assertEqual({q['area'] for q in items}, {'lang','data','math','logic','seq'})
        for q in items:
            self.assertEqual(len(q['c']), 5)
            self.assertEqual(len(set(q['c'])), 5)
            self.assertIn(q['a'], range(5))
            self.assertTrue(q['e'])
            self.assertTrue(q['_meta']['source_basis'])

if __name__ == '__main__': unittest.main()
