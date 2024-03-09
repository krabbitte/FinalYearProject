import music21.stream
from midihandler.midi_handler import MidiHandler
from utilities.utilities import wait_for_input, mido_to_music21, music21_to_mido, get_args
import inquirer
from readchar import key
from mgs.mgs import MGS
from mgs.constants import EDO


class Xentinuator(object):
    def __init__(self, training_path, saved_graphs_path):
        self.midi_handler = MidiHandler()
        self.training_path = training_path
        self.saved_graphs_path = saved_graphs_path

    def user_prompt_ports(self):
        port_names = self.midi_handler.get_midi_port_names()
        questions = [
            inquirer.List('input_port',
                          message="Choose MIDI input port",
                          choices=port_names['inport_names'],
                          ),
            inquirer.List('output_port',
                          message="Choose MIDI output port",
                          choices=port_names['outport_names'],
                          ),
        ]
        answers = inquirer.prompt(questions)
        return [answers['input_port'], answers['output_port']]

    def get_ports(self):
        # Get input/output ports
        inport_name, outport_name = self.user_prompt_ports()
        self.midi_handler.set_ports(inport_name, outport_name)
        self.midi_handler.open_ports()

    def file_mode(self, input_file):
        self.get_ports()
        # Create MGS
        mgs = MGS(EDO.EDO_12, EDO.EDO_22)
        mgs.init_graph(training_path=self.training_path, saved_graphs_path=self.saved_graphs_path)
        mgs.print_graph()
        # Get input file
        mf = music21.converter.parseFile(input_file)
        # Generate output
        output = mgs(mf, EDO.EDO_12)
        midi = music21_to_mido(output)
        # Play output
        self.midi_handler.play_recording(midi)

    def interactive_mode(self):
        self.get_ports()
        while True:
            # start recording
            print('press [space] to start recording or [c] to exit')
            user_input = wait_for_input(key.SPACE, 'c')
            if user_input == key.SPACE:
                self.midi_handler.start_recording()
            elif user_input == 'c':
                break
            # end recording
            print('press [space] to stop recording')
            user_input = wait_for_input(key.SPACE)
            if user_input == key.SPACE:
                self.midi_handler.stop_recording()
            midi = self.midi_handler.get_recording()
            # mf = mido_to_music21(midi)
            # pass music21 representation to MGS
            # midi = music21_to_mido(mf)
            self.midi_handler.play_recording(midi)
        self.midi_handler.exit()

    def test_mode(self):
        self.get_ports()
        # Create MGS
        mgs = MGS(EDO.EDO_12, EDO.EDO_22)
        mgs.init_graph(training_path=self.training_path, saved_graphs_path=self.saved_graphs_path)
        # mgs.print_graph()
        # Create input
        mf = music21.stream.Stream()
        mf.append(music21.note.Note('C4'))
        mf.append(music21.note.Note('E4'))
        mf.append(music21.note.Note('G4'))
        mf.append(music21.chord.Chord(['C4', 'E4', 'G4']))
        # Generate output
        output = mgs(mf, EDO.EDO_12)
        midi = music21_to_mido(output)
        # Play output
        self.midi_handler.play_recording(midi)


if __name__ == '__main__':
    args = get_args()
    xen = Xentinuator(args.training_path, args.saved_graphs_path)
    if args.mode == 'interactive':
        xen.interactive_mode()
    elif args.mode == 'file':
        xen.file_mode(args.input_file)
    elif args.mode == 'test':
        xen.test_mode()
