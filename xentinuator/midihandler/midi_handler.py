import rtmidi
import inquirer
from .recorder.recorder import Recorder


class MidiHandler(object):
    def __init__(self):
        self.__midi_in = rtmidi.MidiIn()
        self.__inport_names = self.__midi_in.get_ports()
        self.__midi_out = rtmidi.MidiOut()
        self.__outport_names = self.__midi_out.get_ports()
        self.__recorder = Recorder()

    def __user_port_selection(self):
        questions = [
            inquirer.List('input_port',
                          message="Choose MIDI input port",
                          choices=self.__inport_names,
                          ),
            inquirer.List('output_port',
                          message="Choose MIDI output port",
                          choices=self.__outport_names,
                          ),
        ]
        answers = inquirer.prompt(questions)
        return [answers['input_port'], answers['output_port']]

    def __open_in_port(self, in_port):
        print("Receiving messages from input port: " + in_port)
        self.__midi_in.open_port(self.__inport_names.index(in_port))

    def __open_out_port(self, out_port):
        print("Sending messages to output port: " + out_port)
        self.__midi_out.open_port(self.__outport_names.index(out_port))

    def play_midi(self, midi):
        self.__midi_out.send_message(midi)

    def setup(self):
        in_port, out_port = self.__user_port_selection()
        self.__open_out_port(out_port)
        self.__midi_in.set_callback(self.__recorder, data=self.__midi_out)
        self.__open_in_port(in_port)

    def start_recording(self):
        print("Starting recording")
        self.__recorder.start_recording()

    def stop_recording(self):
        print("Ending recording")
        self.__recorder.end_recording()

    def get_recording(self):
        return self.__recorder.get_recording()

    def exit(self):
        del self.__midi_out
        del self.__midi_in
