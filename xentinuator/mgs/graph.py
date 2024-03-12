import os
import random
import copy
import re
import music21.converter
from xentinuator.mgs.constants import EDO
from pprint import pprint
from ..utilities.utilities import transpose_stream


class Node(object):
    def __init__(self, name, m21_object=None):
        self.name = name
        self.object = m21_object
        self.links = {}
        self.link_freq = {}
        self.link_freq_buff = {}

    def __str__(self):
        return ''.join(self.name)

    def rand_next(self):
        if len(list(self.links.values())) == 0:
            return None
        # Calculate probabilities based on frequency
        final_freq = {}
        probabilities = {}
        total = 0
        for node_name in self.link_freq:
            buff = self.link_freq_buff[node_name]
            total += self.link_freq[node_name] * buff
            final_freq[node_name] = self.link_freq[node_name] * buff
        for key, value in final_freq.items():
            probabilities[key] = value/total
        # Choose link based on distribution
        key = random.choices(list(probabilities.keys()), weights=list(probabilities.values()))
        return self.links[key[0]]


class Graph(object):
    def __init__(self, edo=EDO.EDO_12, key='C'):
        self.edo = edo
        self.order = 4
        self.key = key
        self.phrase_memory = []
        self.nodes = {}
        self.pointers = {}

    def init_graph(self, training_path='./midi_files/training_corpus/wikifonia/'):
        files = os.listdir(training_path)
        for i in range(0, int(len(files))):
            print('processesing: ', files[i])
            test_file = training_path + '\\' + files[i]
            mf = music21.converter.parseFile(test_file)
            mf = transpose_stream(mf, self.key)
            self.__process_file(mf)

    def __process_file(self, mf):
        if len(mf) == 0:
            return
        m21_objects = mf.flatten().recurse().getElementsByClass(['Note', 'Chord']).stream()
        for i in range(0, len(m21_objects)):
            j = i
            while j >= 0 and j > i - self.order:
                # get sequence
                seq = m21_objects[j:i + 1]
                sequence_name = get_sequence_name(seq, include_note_value=False, include_octave=True)
                sequence_name_detailed = get_sequence_name(seq, include_note_value=True, include_octave=True)
                # create node for sequence
                if sequence_name_detailed not in self.nodes:
                    self.nodes[sequence_name_detailed] = Node(sequence_name_detailed, seq)
                    if sequence_name not in self.pointers:
                        self.pointers[sequence_name] = []
                    self.pointers[sequence_name].append(self.nodes[sequence_name_detailed])
                # get next note
                if i == len(m21_objects) - 1:
                    break
                s = m21_objects[i + 1]
                s_name = get_sequence_name(seq, include_note_value=False, include_octave=True)
                s_name_detailed = get_sequence_name([s], include_note_value=True, include_octave=True)
                # create node for following note
                if s_name_detailed not in self.nodes:
                    self.nodes[s_name_detailed] = Node(s_name, [s])
                    if s_name not in self.pointers:
                        self.pointers[s_name] = []
                    self.pointers[s_name].append(self.nodes[s_name_detailed])
                # create link in sequence for next note or increment frequency
                if s_name_detailed not in self.nodes[sequence_name_detailed].links:
                    self.nodes[sequence_name_detailed].links[s_name_detailed] = self.nodes[s_name_detailed]
                    self.nodes[sequence_name_detailed].link_freq[s_name_detailed] = 1
                    self.nodes[sequence_name_detailed].link_freq_buff[s_name_detailed] = 1
                else:
                    self.nodes[sequence_name_detailed].link_freq[s_name_detailed] += 1
                j -= 1

    def update_graph(self, mf=None):
        if len(mf) == 0:
            return
        mf = transpose_stream(mf, self.key)
        self.__process_file(mf)
        self.phrase_memory.append(mf)

    def bias_graph(self):
        for i in range(len(self.phrase_memory)):
            notes = self.phrase_memory[i].flatten().recurse().getElementsByClass(['Note', 'Chord']).stream()
            seq_size = min(self.order-1, len(notes))
            recency = (i + 1)/len(self.phrase_memory) * 2
            j = 0
            while j + seq_size < len(notes):
                phrase_name = get_sequence_name(notes[j:j + seq_size])
                if phrase_name in self.nodes:
                    current_node = self.nodes[phrase_name]
                    k = j + seq_size
                    while k < len(notes):
                        note_name = get_sequence_name(notes[k])
                        if note_name in current_node.links:
                            current_node.link_freq_buff[note_name] = recency
                            current_node = current_node.links[note_name]
                            k += 1
                        else:
                            break
                j += 1

    def traverse_tree(self, mf):
        mf = mf.flatten().recurse().getElementsByClass(['Note', 'Chord']).stream()
        sub_sequences = []
        sub_sequences_detailed = []
        if len(mf) != 0:
            mf = transpose_stream(mf, self.key)
            sequence_name = get_sequence_name(mf, include_note_value=False)
            sequence_name_detailed = get_sequence_name(mf, include_note_value=True)
            for i in range(0, len(sequence_name)):
                j = i
                while j >= 0 and j > i - self.order:
                    sub_sequences.append(sequence_name[j:i + 1])
                    sub_sequences_detailed.append(sequence_name_detailed[j:i + 1])
                    j -= 1

        output = music21.stream.Stream()
        # find mf sequence in self.nodes
        i = 0
        note = None
        while note is None and i < len(sub_sequences_detailed):
            sub_sequence = random.choice(sub_sequences_detailed)
            if sub_sequence in self.nodes:
                note = self.nodes[sub_sequence]
            i += 1
        i = 0
        # find closest equivalent to mf sequence
        while note is None and i < len(sub_sequences):
            sub_sequence = random.choice(sub_sequences)
            if sub_sequence in self.pointers:
                note = random.choice(self.pointers[sub_sequence])
            i += 1
        # pick a random note
        if note is None:
            note = random.choice(list(self.nodes.values()))

        max_length = 16
        if mf.quarterLength > 0:
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
        print(self.pointers)


def get_sequence_name(seq, include_note_value=True, include_octave=True):
    output = []
    if isinstance(seq, music21.note.Note):
        seq = [seq]
    for i in range(len(seq)):
        name = seq[i].fullName
        if not include_note_value:
            if isinstance(seq[i], music21.chord.Chord):
                delim = '}'
                name = re.split(r'}', name, maxsplit=1)[0] + delim
            elif isinstance(seq[i], music21.note.Note):
                name = seq[i].fullName
                name = re.split(r'(?<=\d)\D', name, maxsplit=1)[0]
        if not include_octave:
            if isinstance(seq[i], music21.chord.Chord):
                split = re.split(r'in octave \d+\s*', name)
                name = ''.join(split)
            elif isinstance(seq[i], music21.note.Note):
                split = re.split(r'in octave \d+\s*', name)
                name = ''.join(split)
        output.append(name)
    return tuple(output)

