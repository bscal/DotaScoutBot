import unittest
import sys, os
sys.path.append(os.path.abspath(os.path.join('..', 'src')))
import gold


class DotaTest(unittest.TestCase):

	def test_gold(self):
		r = gold.get_gold_score(3869)
		print(gold.ESTIMATED_TOTAL)
		self.assertEqual(r, 96.94)


if __name__ == "__main__":
	unittest.main()