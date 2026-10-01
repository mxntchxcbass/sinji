import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('generate_extra', Path(__file__).with_name('generate_extra.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class GeneratorTests(unittest.TestCase):
    def test_reproducible_by_seed(self):
        self.assertEqual(mod.generate(20261001, 10), mod.generate(20261001, 10))

    def test_all_areas_and_count(self):
        bank = mod.generate(4242, 10)
        self.assertEqual(set(bank), set(mod.AREAS))
        self.assertTrue(all(len(bank[a]) == 10 for a in mod.AREAS))

    def test_many_seeds_keep_choices_valid(self):
        for seed in range(100):
            for area, items in mod.generate(seed, 10).items():
                self.assertEqual(len(items), 10)
                for q in items:
                    self.assertEqual(q['area'], area)
                    self.assertEqual(len(q['c']), 5)
                    self.assertEqual(len(set(q['c'])), 5)
                    self.assertTrue(0 <= q['a'] < 5)

    def test_schema_and_answer_ranges(self):
        for area, items in mod.generate(9527, 10).items():
            for q in items:
                self.assertEqual(q['area'], area)
                self.assertEqual(len(q['c']), 5)
                self.assertEqual(len(set(q['c'])), 5)
                self.assertGreaterEqual(q['a'], 0)
                self.assertLess(q['a'], 5)
                self.assertTrue(q['e'])
                self.assertTrue(q['_meta']['difficulty'] in ('기초','표준','도전'))

    def test_each_area_has_balanced_practice_bands(self):
        for items in mod.generate(20261001, 10).values():
            counts = {level: sum(q['_meta']['difficulty'] == level for q in items)
                      for level in ('기초', '표준', '도전')}
            self.assertEqual(counts, {'기초': 4, '표준': 3, '도전': 3})

if __name__ == '__main__':
    unittest.main()
