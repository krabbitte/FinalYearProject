import mido
from asyncio import Lock


class Recorder(object):
    def __init__(self, bpm=180):
        self.__bpm = bpm
        self.__time = 0
        self.__mid = mido.MidiFile()
        self.__track = mido.MidiTrack()
        self.__mid.tracks.append(self.__track)
        self.__lock = Lock()
        self.__is_recording = False

    def __call__(self, event, data=None):
        message, delta_time = event
        self.__time += delta_time
        miditime = round(mido.second2tick(self.__time, self.__mid.ticks_per_beat, mido.bpm2tempo(self.__bpm)))
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
        self.__time = 0

    def start_recording(self):
        self.__time = 0
        self.__is_recording = True

    def end_recording(self):
        self.__is_recording = False
        self.__track.append(mido.MetaMessage('end_of_track'))
        self.__mid.merged_track = mido.merge_tracks(self.__mid.tracks)

    def get_recording(self):
        return self.__mid
