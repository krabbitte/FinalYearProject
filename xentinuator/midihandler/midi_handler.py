import mido
import rtmidi
from xentinuator.recorder.recorder import Recorder


class MidiHandler(object):
    def __init__(self, in_port=None, out_port=None):
        self.__midi_in = rtmidi.MidiIn()
        self.__inport_names = self.__midi_in.get_ports()
        self.__inport_name = in_port
        self.__outport_name = out_port
        self.__midi_out = rtmidi.MidiOut()
        self.__outport_names = self.__midi_out.get_ports()
        self.__recorder = Recorder()
        self.__recordings = []

    def get_midi_port_names(self):
        return {
            "inport_names": self.__midi_in.get_ports(),
            "outport_names": self.__midi_out.get_ports()
        }

    def __open_in_port(self, in_port):
        print("Receiving messages from input port: " + in_port)
        self.__midi_in.open_port(self.__inport_names.index(in_port))

    def __open_out_port(self, out_port):
        print("Sending messages to output port: " + out_port)
        self.__midi_out.open_port(self.__outport_names.index(out_port))

    def set_ports(self, inport_name, outport_name):
        self.__inport_name = inport_name
        self.__outport_name = outport_name

    def open_ports(self):
        if self.__inport_name is None or self.__outport_name is None:
            raise Exception("Cannot open ports: No ports are set")
        self.__open_out_port(self.__outport_name)
        self.__midi_in.set_callback(self.__recorder, data=self.__midi_out)
        self.__open_in_port(self.__inport_name)

    def load_file(self):
        midi_file = mido.MidiFile('testfile.mid')
        self.__recordings.append(midi_file)

    def start_recording(self):
        print("Starting recording")
        self.__recorder.start_recording()

    def stop_recording(self):
        print("Ending recording")
        recording = self.__recorder.end_recording()
        self.__recordings.append(recording)

    def get_recording(self, index=-1):
        return self.__recordings[index]

    def get_recordings(self):
        return self.__recordings

    def play_recording(self, midi):
        try:
            for msg in midi.play():
                self.__midi_out.send_message(msg.bytes())
        except KeyboardInterrupt:
            return

    def exit(self):
        del self.__midi_out
        del self.__midi_in
