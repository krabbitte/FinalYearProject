import os
import pickle
from datetime import datetime
from xentinuator.mgs.graph import Graph
from xentinuator.mgs.constants import EDO
import sys

sys.setrecursionlimit(10000)


class MGS(object):
    def __init__(self, source_edo=EDO.EDO_12, target_edo=EDO.EDO_12):
        self.__source_edo = source_edo
        self.__target_edo = target_edo
        self.__graph = None

    def init_graph(self, training_path, saved_graphs_path):
        if saved_graphs_path is None:
            self.__graph = Graph(edo=self.__source_edo, key='D')
            self.__graph.init_graph(training_path)
            self.__save_graph()
        else:
            files = os.listdir(saved_graphs_path)
            with open(saved_graphs_path + files[0], 'rb') as f:
                self.__graph = pickle.load(f)

    def __save_graph(self, saved_graphs_path='./saved_graphs/'):
        with open(saved_graphs_path + datetime.now().strftime("%m-%d-%YT%H-%M-%S"), 'wb') as f:
            pickle.dump(self.__graph, f, pickle.HIGHEST_PROTOCOL)

    def __generate(self, mf):
        self.__graph.update_graph(mf)
        return self.__graph.traverse_tree(mf)

    def print_graph(self):
        print(self.__graph.print_graph())

    def __call__(self, mf, target_edo=None):
        # Update Markov Chain with data from new phrase
        self.__graph.update_graph(mf)
        # Generate output
        output = self.__generate(mf)
        return output
