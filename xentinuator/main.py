from midihandler.midi_handler import MidiHandler
from datetime import datetime
import inquirer
from readchar import readkey, key


def wait_for_input(*keys):
    while True:
        user_input = readkey()
        for i in keys:
            if user_input == i:
                return i


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

    def __call__(self):
        inport_name, outport_name = self.user_prompt_ports()
        self.midi_handler.set_ports(inport_name, outport_name)
        self.midi_handler.open_ports()
        while True:
            print('press [space] to start recording or [c] to exit')
            user_input = wait_for_input(key.SPACE, 'c')
            if user_input == key.SPACE:
                self.midi_handler.start_recording()
            elif user_input == 'c':
                break

            print('press [space] to stop recording')
            user_input = wait_for_input(key.SPACE)
            if user_input == key.SPACE:
                self.midi_handler.stop_recording()
            midi = self.midi_handler.get_recording()

            self.midi_handler.play_recording(midi)

        self.midi_handler.exit()


if __name__ == '__main__':
    xen = Xentinuator()
    xen()
