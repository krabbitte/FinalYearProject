from xentinuator.mgs.constants import EDO

class Xenharmonizer(object):
    def __init__(self):
        pass

    def __call__(self, mf, target_edo=EDO.EDO_12):
        m21_objects = mf.flatten().recurse().getElementsByClass(['Note', 'Chord']).stream()
        for m21_object in m21_objects:
            print(m21_object.fullName)
        return mf