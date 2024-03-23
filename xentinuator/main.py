import music21.stream
from midihandler.midi_handler import MidiHandler
from utilities.utilities import wait_for_input, mido_to_music21, music21_to_mido, get_args
import inquirer
from readchar import key
from mgs.mgs import MGS
from mgs.constants import EDO


class Xentinuator(object):
    def __init__(self, training_path, saved_graphs_path, source_edo=EDO.EDO_12, target_edo=EDO.EDO_12):
        self.midi_handler = MidiHandler()
        self.training_path = training_path
        self.saved_graphs_path = saved_graphs_path
        self.source_edo = source_edo
        self.target_edo = target_edo

    def user_prompt_ports(self):
        # Prompt the user to select from the available MIDI ports.
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
        # Get and set input/output ports.
        inport_name, outport_name = self.user_prompt_ports()
        self.midi_handler.set_ports(inport_name, outport_name)
        self.midi_handler.open_ports()

    def file_mode(self, input_file):
        self.get_ports()
        # Create and initialize MGS.
        mgs = MGS(self.source_edo, self.target_edo)
        mgs.init_graph(training_path=self.training_path, saved_graphs_path=self.saved_graphs_path)
        # Get and parse the input midi file into its music21 representation.
        mf = music21.converter.parseFile(input_file)
        # Generate output using input.
        output = mgs(mf)
        midi = music21_to_mido(output)
        # Play output via midi output port.
        self.midi_handler.play_recording(midi)

    def interactive_mode(self):
        self.get_ports()

        # Create and initialize MGS.
        mgs = MGS(self.source_edo, self.target_edo)
        mgs.init_graph(training_path=self.training_path, saved_graphs_path=self.saved_graphs_path)

        # Begin main interaction loop.
        while True:
            # Prompt user to start recording/save progress/exit program.
            print('[space] to start recording - [x] to save graph - [c] to exit')
            user_input = wait_for_input(key.SPACE, 'c', 'x')
            if user_input == key.SPACE:
                self.midi_handler.start_recording()
            elif user_input == 'x':
                mgs.save_graph()
            elif user_input == 'c':
                break

            # Prompt user to end recording.
            print('press [space] to stop recording')
            user_input = wait_for_input(key.SPACE)
            if user_input == key.SPACE:
                self.midi_handler.stop_recording()
            midi = self.midi_handler.get_recording()
            mf = mido_to_music21(midi)

            # Pass input to MGS and generate output
            output = mgs(mf)
            midi = music21_to_mido(output)

            # Play generated output.
            self.midi_handler.play_recording(midi)
        self.midi_handler.exit()

    def test_mode(self):
        self.get_ports()
        # Create and initialize MGS.
        mgs = MGS(self.source_edo, self.target_edo)
        mgs.init_graph(training_path=self.training_path, saved_graphs_path=self.saved_graphs_path)
        # Create test input
        mf = music21.stream.Stream()
        mf.append(music21.note.Note('C4'))
        mf.append(music21.note.Note('E4'))
        mf.append(music21.note.Note('G4'))
        mf.append(music21.chord.Chord(['C4', 'E4', 'G4']))
        mf.append(music21.note.Note('G4'))
        mf.append(music21.note.Note('E4'))
        mf.append(music21.note.Note('C4'))
        # Pass input to MGS and generate output
        output = mgs(mf)
        midi = music21_to_mido(output)
        # Play generated output.
        self.midi_handler.play_recording(midi)


if __name__ == '__main__':
    args = get_args()
    xen = Xentinuator(args.training_path, args.saved_graphs_path, args.source_edo, args.target_edo)
    if args.mode == 'interactive':
        xen.interactive_mode()
    elif args.mode == 'file':
        xen.file_mode(args.input_file)
    elif args.mode == 'test':
        xen.test_mode()
