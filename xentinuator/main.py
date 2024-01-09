from midihandler.midi_handler import MidiHandler
import inquirer


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
            input("Press [space] to start recording")
            self.midi_handler.start_recording()
            input("Press [space] to stop recording")
            self.midi_handler.stop_recording()
            self.midi_handler.play_recording()


if __name__ == '__main__':
    xen = Xentinuator()
    xen()
