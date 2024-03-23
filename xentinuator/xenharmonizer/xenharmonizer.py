import math
import music21.pitch
from xentinuator.mgs.constants import EDO


def get_closest_pitch(pitch_array, pitch):
    left = 0
    right = len(pitch_array) - 1
    mid = None
    while left <= right:
        mid = left + (right - left) // 2
        if pitch_array[mid] == pitch:
            return pitch_array[mid]
        elif pitch_array[mid] < pitch:
            left = mid + 1
        else:
            right = mid - 1
    return pitch_array[mid]


def convert_to_edo(mf, target_edo):
    edo_pitches = []
    max_pitch = music21.note.Note(midi=127).pitch.frequency
    current_pitch = music21.note.Note(midi=0).pitch.frequency
    ratio = math.pow(2, 1 / target_edo)
    # Calculate target EDO pitches.
    while current_pitch <= max_pitch:
        current_pitch *= ratio
        edo_pitches.append(current_pitch)
    m21_objects = mf.flatten().recurse().getElementsByClass(['Note', 'Chord']).stream()
    for i in range(len(m21_objects)):
        if isinstance(m21_objects[i], music21.note.Note):
            # Convert note to the closest target EDO pitch.
            closest_pitch = get_closest_pitch(edo_pitches, m21_objects[i].pitch.frequency)
            m21_objects[i].pitch.frequency = closest_pitch
        elif isinstance(m21_objects[i], music21.chord.Chord):
            # Convert notes from chord to the closest target EDO pitch.
            for j in range(len(m21_objects[i].notes)):
                closest_pitch = get_closest_pitch(edo_pitches, m21_objects[i].notes[j].pitch.frequency)
                m21_objects[i].notes[j].pitch.frequency = closest_pitch
    return mf


class Xenharmonizer(object):
    def __init__(self):
        self.edos = {
            EDO.EDO_12.name: 12,
            EDO.EDO_22.name: 22,
            EDO.EDO_31.name: 31,
        }

    def __call__(self, mf, source_edo=EDO.EDO_12, target_edo=EDO.EDO_12):
        mf = convert_to_edo(mf, self.edos[target_edo.name])
        return mf
