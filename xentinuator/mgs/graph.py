import os
import random
import copy
import re
import music21.converter
from pprint import pprint
from ..utilities.utilities import transpose_stream


class Node(object):
    def __init__(self, name, m21_object=None):
        self.name = name
        self.object = m21_object
        self.links = {}
        self.link_freq = {}

    def __str__(self):
        return ''.join(self.name)

    def rand_next(self):
        if len(list(self.links.values())) == 0:
            return None
        # Calculate probabilities based on frequency
        probabilities = {}
        total = sum(self.link_freq.values())
        for key, value in self.link_freq.items():
            probabilities[key] = value/total
        # Choose link based on distribution
        key = random.choices(list(probabilities.keys()), weights=list(probabilities.values()))
        return self.links[key[0]]


class Graph(object):
    def __init__(self, edo, key='C'):
        self.edo = edo
        self.order = 4
        self.key = key
        self.phrase_memory = []
        self.nodes = {}

    def init_graph(self, training_path='./midi_files/training_corpus/wikifonia/'):
        files = os.listdir(training_path)
        for i in range(0, int(len(files))):
            print('processesing: ', files[i])
            test_file = training_path + '\\' + files[i]
            mf = music21.converter.parseFile(test_file)
            mf = transpose_stream(mf, self.key)
            self.__process_file(mf)

    def update_graph(self, mf):
        mf = transpose_stream(mf, self.key)
        self.__process_file(mf)
        self.phrase_memory.append(mf)

    def __process_file(self, mf):
        m21_objects = mf.flatten().recurse().getElementsByClass(['Note', 'Chord']).stream()
        print('Length: ', len(m21_objects))
        for i in range(0, len(m21_objects)):
            print('processing ', i)
            j = i
            while j >= 0 and j > i - self.order:
                # get sequence
                seq = m21_objects[j:i + 1]
                sequence_name = get_sequence_name(seq)
                # create node for sequence
                if sequence_name not in self.nodes:
                    self.nodes[sequence_name] = Node(sequence_name, seq)
                # get next note
                if i == len(m21_objects) - 1:
                    break
                s = m21_objects[i + 1]
                s_name = get_sequence_name([s])
                # create node for following note
                if s_name not in self.nodes:
                    self.nodes[s_name] = Node(s_name, [s])
                # create link in sequence for next note or increment frequency
                if s.fullName not in self.nodes[sequence_name].links:
                    self.nodes[sequence_name].links[s_name] = self.nodes[s_name]
                    self.nodes[sequence_name].link_freq[s_name] = 1
                else:
                    self.nodes[sequence_name].link_freq[s_name] += 1
                j -= 1

    def bias_graph(self):
        for node in list(self.nodes.values()):
            for phrase in self.phrase_memory:
                notes = phrase.flatten().recurse().getElementsByClass(['Note', 'Chord']).stream()
                for note in notes:
                    if note.fullName in node.link_freq:
                        node.link_freq[note.fullName] *= 2

    def traverse_tree(self, mf):
        mf = transpose_stream(mf, self.key)
        name = get_sequence_name(mf)
        sub_sequences = []
        for i in range(0, len(name)):
            j = i
            while j >= 0 and j > i - self.order:
                sub_sequences.append(name[j:i + 1])
                j -= 1

        output = music21.stream.Stream()

        # find mf sequence in self.nodes or closest equivalent
        i = 0
        note = None
        while note is None and i < len(sub_sequences):
            sub_sequence = random.choice(sub_sequences)
            if sub_sequence in self.nodes:
                note = self.nodes[sub_sequence]
            i += 1

        if note is None:
            note = random.choice(self.nodes.values())

        max_length = mf.quarterLength * 10
        current_length = 0
        while current_length < max_length and note is not None:
            for note_object in note.object:
                current_length += note_object.quarterLength
            output.append(copy.deepcopy(note.object))
            note = note.rand_next()
        return output

    def print_graph(self):
        print(self.nodes)


def get_sequence_name(seq, include_note_value=True):
    output = []
    for i in range(len(seq)):
        name = seq[i].fullName
        if not include_note_value:
            if isinstance(seq[i], music21.chord.Chord):
                delim = '}'
                name = re.split(r'}', name, maxsplit=1)[0] + delim
                print(name)
            elif isinstance(seq[i], music21.note.Note):
                name = seq[i].fullName
                name = re.split(r'(?<=\d)\D', name, maxsplit=1)[0]
        output.append(name)
    return tuple(output)

