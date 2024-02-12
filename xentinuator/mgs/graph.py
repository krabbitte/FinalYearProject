import os
import random
import copy
import music21.converter
from ..utilities.utilities import transpose_stream


class Node(object):
    def __init__(self, m21_object=None, name=''):
        self.name = name
        self.object = m21_object
        self.links = {}
        self.link_freq = {}

    def __str__(self):
        return self.name

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
        self.__max_rest_duration = 1.5
        self.m21_objects = None
        self.order = 4
        self.key = key
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
        self.__process_file(mf)

    def __process_file(self, mf):
        self.m21_objects = mf.flatten().recurse().getElementsByClass(['Note', 'Chord']).stream()
        for i in range(0, len(self.m21_objects)):
            j = i
            while j >= 0 and j > i - self.order:
                # get sequence
                seq = self.m21_objects[j:i + 1]
                sequence_name = get_sequence_name(seq)
                # get next note
                if i == len(self.m21_objects) - 1:
                    break
                s = self.m21_objects[i + 1]
                # create node for sequence
                if sequence_name not in self.nodes:
                    self.nodes[sequence_name] = Node(seq, sequence_name)
                # create node for following note
                if s.fullName not in self.nodes:
                    self.nodes[s.fullName] = Node([s], s.fullName)
                # create link in sequence for next note or increment frequency
                if s.fullName not in self.nodes[sequence_name].links:
                    self.nodes[sequence_name].links[s.fullName] = self.nodes[s.fullName]
                    self.nodes[sequence_name].link_freq[s.fullName] = 1
                else:
                    self.nodes[sequence_name].link_freq[s.fullName] += 1
                j -= 1

    def traverse_tree(self, mf):
        output = music21.stream.Stream()
        # find mf sequence in self.nodes or closest equivalent and bias probabilities
        note = random.choice(list(self.nodes.values()))
        while note is not None:
            output.append(copy.deepcopy(note.object))
            note = note.rand_next()
        return output

    def print_graph(self):
        print(self.nodes)


def get_sequence_name(seq):
    name = ''
    for i in range(len(seq)):
        name += seq[i].fullName + (' | ' if i < len(seq) - 1 else '')
    return name

