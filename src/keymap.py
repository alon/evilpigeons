# Copyright Evil Pegions team Global Game Jam 2010:
#  Simon Reisman
#  Omer Nainudel
#  Ori Cohen
#  Alon Levy

class KeyMap(object):

    IGNORE_MOD = -1

    def __init__(self):
        self._map = {}
        self._map_mod_set = {}

    def add(self, key, func, mod = IGNORE_MOD):
        if key not in self._map:
            self._map[key] = [(mod, func)]
            self._map_mod_set[key] = set([mod])
        else:
            existing = self._map[key]
            if mod in self._map_mod_set[key]:
                # just replace the existing one - trust the order is already fine
                done = False
                for i, (e_mod, e_func) in enumerate(existing):
                    if e_mod == mod:
                        existing[i] = (mod, func)
                        done = True
                    #print "replaced %s -> %s" % (e_func, func)
                assert(done)
                return
            self._map_mod_set[key].add(mod)
            print "adding %s, %s, %s" % (key, func, mod)
            at_i = 0 # default - put at the end
            # keep it sorted: most strict first
            if mod == self.IGNORE_MOD:
                at_i = len(existing)
            elif mod == 0:
                # put after IGNORE_MOD
                at_i = 0
                for i, (e_mod, e_func) in enumerate(existing):
                    if e_mod == self.IGNORE_MOD:
                        at_i = i + 1
            existing.insert(at_i, (mod, func))

    def onkey(self, key, mod):
        if key in self._map:
            for f_mod, func in self._map[key]:
                if f_mod == self.IGNORE_MOD or (not mod and not f_mod) or (mod & f_mod):
                    return func() # takes the first
        return None

    def __len__(self):
        return sum(len(v) for v in self._map.values())

    def __str__(self):
        s = []
        for key in self._map:
            s.append('key %s -> %s' % (key, self._map[key]))
        return '\n'.join(s)

    __repr__ = __str__

