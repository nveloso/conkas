from sym_exec.utils import is_concrete, is_symbolic


class Registers(object):
    def __init__(self, registers=None):
        if registers is None:
            registers = {}
        self._registers = registers

    def __repr__(self):
        return 'Registers()'

    def __str__(self):
        return str(self._registers)

    def set(self, idx, val):
        assert (idx >= 0)

        if is_concrete(val):
            val = val.to_bytes(32, byteorder='big')

        self._registers[idx] = val

    def get(self, idx):
        assert (idx >= 0)

        val = self._registers.get(idx)
        if val is None:
            return

        if is_symbolic(val):
            return val

        assert (len(val) == 32)

        return int.from_bytes(val, byteorder='big')

    def __copy__(self):
        return Registers(self._registers.copy())
