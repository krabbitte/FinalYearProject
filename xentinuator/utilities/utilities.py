import io
import mido
import music21
import argparse
from xentinuator.mgs.constants import EDO
from readchar import readkey


def int_to_edo(num):
    edos = {
        12: EDO.EDO_12,
        22: EDO.EDO_22,
        31: EDO.EDO_31
    }
    return edos[num]


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-mode", help="interactive, file, test.", type=str, required=True)
    parser.add_argument("-training_path", help="Path of the training corpus.", type=str, required=False)
    parser.add_argument("-saved_graphs_path", help="Path to previously trained graphs", type=str, required=False)
    parser.add_argument("-input_file", help="Path to an input file used to generate music.", type=str, required=False)
    parser.add_argument("-source_edo", help="Source tuning system.", default=12, type=int, required=False)
    parser.add_argument("-target_edo", help="Target number of divisions of the octave.", default=12, type=int, required=False)
    args = parser.parse_args()
    args.source_edo = int_to_edo(args.source_edo)
    args.target_edo = int_to_edo(args.target_edo)
    return args


def wait_for_input(*keys):
    while True:
        user_input = readkey()
        for i in keys:
            if user_input == i:
                return i


def transpose_stream(mf, target_key):
    notes = mf.flatten().recurse().getElementsByClass(['Note']).stream()
    if len(notes) < 4:
        return mf
    key = notes.analyze('key')
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
