import os
import random
import copy
import music21.converter


class Node(object):
    def __init__(self, m21_object=None, name=''):
        self.name = name
        self.object = m21_object
        self.links = {}
        self.link_freq = {}

    def __str__(self):
        return self.name

    def rand_next(self):
        if len(self.links.values()) == 0:
            return None
        probabilities = {}
        total = sum(self.link_freq.values())
        for key, value in self.link_freq.items():
            probabilities[key] = value/total
        key = random.choices(list(probabilities.keys()), weights=probabilities.values())
        return self.links[key[0]]


def get_index(list, item):
    for i in range(list):
        if item == list[i]:
            return i
    return -1


def get_sequence_name(seq):
    name = ''
    for i in range(len(seq)):
        name += seq[i].fullName + (' | ' if i < len(seq) - 1 else '')
    return name


class Graph(object):
    def __init__(self, edo):
        self.edo = edo
        self.__max_rest_duration = 1.5
        self.m21_objects = None
        self.order = 4
        self.nodes = {}

    def init_graph(self, training_path='./midi_files/training_corpus/wikifonia/'):
        files = os.listdir(training_path)
        for i in range(0, int(len(files))):
            test_file = training_path + '\\' + files[i]
            print('processesing: ', files[i])
            mf = music21.converter.parseFile(test_file)
            self.process_file(mf)

    def process_file(self, mf):
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
        out = music21.stream.Stream()
        note = random.choice(list(self.nodes.values()))
        while note is not None:
            out.append(copy.deepcopy(note.object))
            note = note.rand_next()
        return out

    def print_graph(self):
        print(self.nodes)
