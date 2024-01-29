import os
import random

import music21.converter


class Node(object):
    def __init__(self, m21_object=None, name=''):
        self.name = name
        self.object = m21_object
        self.children = {}

    def __str__(self):
        out = ''
        stack = [[-1, self]]
        while len(stack) > 0:
            level, item = stack.pop()
            out += ' '*level + (str(item.object.pitch) if item.object is not None else '') + '\n'
            for _, value in item.children.items():
                stack.append([level + 1, value])
        return out


class Graph(object):
    def __init__(self, edo):
        self.edo = edo
        self.__max_rest_duration = 1.5
        self.root_node = Node(name='root')

    def init_graph(self, training_path='./midi_files/training_corpus/'):
        files = os.listdir(training_path)
        for i in range(0, int(len(files))):
            test_file = training_path + '\\' + files[i]
            print('processesing: ', files[i])
            self.process_file(test_file)

    def process_file(self, file_path):
        mf = music21.converter.parseFile(file_path)
        m21_objects = mf.flatten().recurse()
        stack = m21_objects.getElementsByClass(['Note', 'Rest']).stream()
        current_node = self.root_node
        try:
            while len(stack) > 0:
                m21_object = stack.pop(0)
                if m21_object.classes[0] == 'Note':
                    # check children of object for pitch
                    while str(m21_object.pitch)[:-1] in current_node.children:
                        # progress graph phrase
                        current_node = current_node.children[str(m21_object.pitch)[:-1]]
                        # get next note
                        m21_object = stack.pop(0)
                        rest_duration = 0
                        while m21_object.classes[0] == 'Rest':
                            m21_object = stack.pop(0)
                            rest_duration += m21_object.duration.quarterLength.real
                        if rest_duration > self.__max_rest_duration:
                            current_node = self.root_node
                    # progressed to leaf - add note
                    if str(m21_object.pitch)[:-1] not in current_node.children:
                        current_node.children[str(m21_object.pitch)[:-1]] = Node(m21_object)
                        current_node = current_node.children[str(m21_object.pitch)[:-1]]
                elif m21_object.classes[0] == 'Rest':
                    rest_duration = 0
                    while m21_object.classes[0] == 'Rest':
                        m21_object = stack.pop(0)
                        rest_duration += m21_object.duration.quarterLength.real
                    if rest_duration > self.__max_rest_duration:
                        current_node = self.root_node
        except IndexError:
            pass

    def traverse_tree(self, mf):
        m21_stack = mf.flatten().recurse().getElementsByClass(['Note']).stream()

        phrase = music21.stream.Stream()
        current_node = self.root_node
        while len(m21_stack) > 0:
            m21_object = m21_stack.pop(0)
            if str(m21_object.pitch)[:-1] in current_node.children:
                if current_node.object is not None:
                    phrase.append(current_node.object)
                current_node = current_node.children[str(m21_object.pitch)[:-1]]
            else:
                break

        while len(list(current_node.children.values())) > 0:
            current_node = random.choice(list(current_node.children.values()))
            phrase.append(current_node.object)

        return phrase

    def print_graph(self):
        print(self.root_node)

