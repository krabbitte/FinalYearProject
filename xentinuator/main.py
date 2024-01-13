import mido
from midihandler.midi_handler import MidiHandler
from utilities.utilities import wait_for_input, mido_to_music21, music21_to_mido
import inquirer
from readchar import key


class Xentinuator(object):
    def __init__(self):
        self.midi_handler = MidiHandler()

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

    def file_mode(self):
        inport_name, outport_name = self.user_prompt_ports()
        self.midi_handler.set_ports(inport_name, outport_name)
        self.midi_handler.open_ports()

        midi = mido.MidiFile('./midi_files/b.mid')
        mf = mido_to_music21(midi)
        midi = music21_to_mido(mf)

        self.midi_handler.play_recording(midi)

    def interactive_mode(self):
        inport_name, outport_name = self.user_prompt_ports()
        self.midi_handler.set_ports(inport_name, outport_name)
        self.midi_handler.open_ports()
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
            mf = mido_to_music21(midi)
            # pass music21 representation to MGS
            midi = music21_to_mido(mf)
            self.midi_handler.play_recording(midi)
        self.midi_handler.exit()


if __name__ == '__main__':
    xen = Xentinuator()
    # xen.interactive_mode()
    xen.file_mode()
