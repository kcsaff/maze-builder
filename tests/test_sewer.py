import unittest
from maze_builder.sewer import Choice


class TestChoice(unittest.TestCase):
    def test_weighting(self):
        choice = Choice.of({'FOO': 'foo', 'BAR': 'bar'}).weighting('baz', {'foo': 10, 'bar': 0})
        self.assertEqual(choice('baz'), 'FOO')

        choice = Choice.of({'FOO': 'foo', 'BAR': 'bar'}).weighting('baz', {'foo': 0, 'bar': 10})
        self.assertEqual(choice('baz'), 'BAR')


if __name__ == '__main__':
    unittest.main()