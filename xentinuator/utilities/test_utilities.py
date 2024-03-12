import unittest
import music21
import utilities

class MyTestCase(unittest.TestCase):
    def test_transpose_stream(self):
        mf = music21.stream.Stream()
        mf.append(music21.note.Note('C4'))
        mf = utilities.transpose_stream(mf, 'C')
        for m21_object in mf:
            print(m21_object.fullName)
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
