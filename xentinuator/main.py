from midihandler.midi_handler import MidiHandler


class Xentinuator(object):
    def __init__(self):
        self.midi_handler = MidiHandler()
        self.midi_handler.setup()

        # loop

        input("Press [space] to start recording")
        self.midi_handler.start_recording()
        input("Press [space] to stop recording")
        self.midi_handler.stop_recording()
        recording = self.midi_handler.get_recording()
        print(recording)

        # play


if __name__ == '__main__':
    Xentinuator()
