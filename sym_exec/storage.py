from sym_exec.utils import is_concrete, is_symbolic


class Storage(object):
    def __init__(self, storage=None):
        if storage is None:
            storage = {}
        self._storage = storage

    def __repr__(self):
        return 'Storage()'

    def __str__(self):
        return str(self._storage)

    def set(self, key, value):
        if is_concrete(key):
            assert (key >= 0)

        if is_concrete(value):
            value = value.to_bytes(32, byteorder='big')

        if not self._storage.get(key):
            self._storage[key] = []

        self._storage[key].append(value)

    def get(self, key, ssa_position=-1):
        if is_concrete(key):
            assert (key >= 0)

        value = self._storage.get(key)
        if not value:
            return

        try:
            value = value[ssa_position]
        except IndexError:
            return
        if is_symbolic(value):
            return value

        assert (len(value) == 32)

        return int.from_bytes(value, byteorder='big')

    def __copy__(self):
        new_storage = self._storage.copy()
        for key, value in new_storage.items():
            new_storage[key] = value.copy()
        return Storage(new_storage)
