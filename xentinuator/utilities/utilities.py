import io
import mido
import music21
from readchar import readkey


@staticmethod
def wait_for_input(*keys):
    while True:
        user_input = readkey()
        for i in keys:
            if user_input == i:
                return i


@staticmethod
def mido_to_music21(midi):
    f = io.BytesIO()
    midi.save(file=f)
    f.seek(0)
    mf = music21.converter.parseData(f.read())
    return mf


@staticmethod
def music21_to_mido(mf):
    mf = music21.midi.translate.streamToMidiFile(mf)
    mf_bytes = mf.writestr()
    fp = io.BytesIO(mf_bytes)
    midi = mido.MidiFile(file=fp)
    return midi
