import io
import mido
import music21
import argparse
from readchar import readkey


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-mode", help="interactive, file, test.", type=str, required=True)
    parser.add_argument("-training_path", help="Path of the training corpus.", type=str, required=False)
    parser.add_argument("-saved_graphs_path", help="Path to previously trained graphs", type=str, required=False)
    parser.add_argument("-input_file", help="Path to an input file used to generate music.", type=str, required=False)
    args = parser.parse_args()
    return args


def wait_for_input(*keys):
    while True:
        user_input = readkey()
        for i in keys:
            if user_input == i:
                return i


def transpose_stream(mf, target_key):
    notes = mf.flatten().recurse().getElementsByClass(['Note']).stream()
    key = notes.analyze('key')
    print(key.tonic)
    interval = music21.interval.Interval(key.tonic, music21.pitch.Pitch(target_key))
    mf = mf.transpose(interval)
    return mf


def mido_to_music21(midi):
    f = io.BytesIO()
    midi.save(file=f)
    f.seek(0)
    mf = music21.converter.parseData(f.read())
    return mf


def music21_to_mido(mf):
    mf = music21.midi.translate.streamToMidiFile(mf)
    mf_bytes = mf.writestr()
    fp = io.BytesIO(mf_bytes)
    midi = mido.MidiFile(file=fp)
    return midi
