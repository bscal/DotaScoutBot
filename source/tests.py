import unittest
import gold


class DotaTest(unittest.TestCase):

	def test_gold(self):
		r = gold.get_gold_score(3869)
		self.assertEqual(r, 103.15)


if __name__ == "__main__":
	unittest.main()