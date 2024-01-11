from datetime import datetime
import mido
import xentinuator.recorder.constants as constants


class Recorder(object):
    def __init__(self):
        self.__time = 0
        self.__mid = mido.MidiFile()
        self.__track = mido.MidiTrack()
        self.__mid.tracks.append(self.__track)
        self.__is_recording = False
        self.__starting = False

    def __call__(self, event, data=None):
        message, delta_time = event
        if self.__starting:
            self.__time = 0
            self.__starting = False
        else:
            self.__time = delta_time
        miditime = round(mido.second2tick(self.__time, self.__mid.ticks_per_beat, constants.TEMPO))
        if data is not None:
            data.send_message(message)
        if self.__is_recording:
            if message[0] != 254:
                if 127 < message[0] < 144:
                    msg = mido.Message('note_off', note=message[1], velocity=message[2], time=miditime)
                    self.__track.append(msg)
                elif 143 < message[0] < 160:
                    msg = mido.Message('note_on', note=message[1], velocity=message[2], time=miditime)
                    self.__track.append(msg)

    def start_recording(self):
        self.__starting = True
        self.__is_recording = True

    def clear_recording(self):
        self.__mid = mido.MidiFile()
        self.__track = mido.MidiTrack()
        self.__mid.tracks.append(self.__track)

    def end_recording(self):
        self.__is_recording = False
        self.__track.append(mido.MetaMessage('end_of_track'))
        self.__mid.merged_track = mido.merge_tracks(self.__mid.tracks)
        self.__mid.filename = datetime.now().strftime("%m-%d-%YT%H:%M:%S")
        recording = self.__mid
        self.clear_recording()
        return recording
