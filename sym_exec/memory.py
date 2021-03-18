from z3 import Extract, BitVecVal, Concat, simplify

from sym_exec.utils import is_concrete, is_symbolic, ceil32


class Memory(object):
    def __init__(self, memory=None, size=0):
        if memory is None:
            memory = {}
        self._memory = memory
        self._size = size

    def __repr__(self):
        return 'Memory()'

    def __str__(self):
        return str(self._memory)

    @property
    def size(self):
        return self._size

    def extend(self, start_position: int, size: int):
        if size == 0:
            return

        new_size = ceil32(start_position + size)
        if new_size <= self._size:
            return
        size_to_extend = new_size - self._size
        self._size += size_to_extend

    def store(self, start_position, value, size: int = 32):
        if size == 0:
            return

        if is_concrete(value):
            value = value & ((2 ** (size * 8)) - 1)
            _bytes = value.to_bytes(size, byteorder="big")
        else:
            bv_size = value.size()
            assert (bv_size // 8) >= size

            _bytes = []
            end = bv_size - (size * 8) - 1
            for i in range(bv_size - 1, end, -8):
                _bytes.append(Extract(i, i - 7, value))
        assert len(_bytes) == size

        if is_symbolic(start_position):
            for i in range(size):
                position = simplify(start_position + i)
                if not self._memory.get(position):
                    self._memory[position] = []
                self._memory[position].append(_bytes[i])
            return

        if start_position >= self._size:
            return

        end = start_position + size
        _bytes_idx = 0
        for i in range(self._size):
            if not self._memory.get(i):
                self._memory[i] = []
            if start_position <= i < end:
                self._memory[i].append(_bytes[_bytes_idx])
                _bytes_idx += 1
            else:
                self._memory[i].append(self._memory[i][-1] if len(self._memory[i]) > 0 else 0)

    def load(self, start_position, size=32, read_as_bytes=False, ssa_position=-1):
        position_is_symbolic = is_symbolic(start_position)
        symbolic_load = False
        symbolic_starts_idx = 0
        ret = []
        for i in range(size):
            start = start_position + i
            if position_is_symbolic:
                value = self._memory.get(simplify(start), 0)
            elif start < self._size:
                value = self._memory.get(start, 0)
            else:
                break

            if value != 0:
                value = value[ssa_position]
            if not symbolic_load and is_symbolic(value):
                symbolic_load = True
                symbolic_starts_idx = i
            elif symbolic_load and is_concrete(value):
                value = BitVecVal(value, 8)

            ret.append(value)

        for i in range(symbolic_starts_idx):
            ret[i] = BitVecVal(ret[i], 8)

        if symbolic_load:
            if len(ret) > 1:
                return simplify(Concat(ret))
            return simplify(ret[0])
        if read_as_bytes:
            return bytes(ret)
        return int.from_bytes(ret, byteorder='big')

    def __copy__(self):
        new_memory = self._memory.copy()
        for key, value in new_memory.items():
            new_memory[key] = value.copy()
        return Memory(new_memory, self._size)
