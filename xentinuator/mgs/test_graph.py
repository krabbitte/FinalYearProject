import unittest
import xentinuator.mgs.graph as graph
import music21

class MyTestCase(unittest.TestCase):
    def test_process_file(self):
        new_graph = graph.Graph()
        mfA = music21.stream.Stream()
        mfA.append(music21.note.Note('C4', type='quarter'))
        mfA.append(music21.note.Note('E4'))
        mfA.append(music21.note.Note('G4'))
        mfA.append(music21.note.Note('B4'))
        mfA.append(music21.chord.Chord(['C4', 'E4', 'G4']))
        new_graph.update_graph(mfA)

        mfB = music21.stream.Stream()
        mfB.append(music21.note.Note('C4', type='eighth'))
        output = new_graph.traverse_tree(mfB)
        for m21_object in output:
            print(m21_object.fullName)

    def test_get_sequence_name(self):
        mf = music21.stream.Stream()
        mf.append(music21.note.Note('C4'))
        mf.append(music21.note.Note('E4'))
        mf.append(music21.note.Note('G4'))
        mf.append(music21.note.Note('B4'))
        mf.append(music21.chord.Chord(['C4', 'E4', 'G4']))
        print(graph.get_sequence_name(mf))
        print(graph.get_sequence_name(mf, include_note_value=False))
        print(graph.get_sequence_name(mf, include_octave=False))
        print(graph.get_sequence_name(mf, include_note_value=False, include_octave=False))
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
