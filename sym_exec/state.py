from copy import copy

from sym_exec.environment import Environment
from sym_exec.memory import Memory
from sym_exec.registers import Registers
from sym_exec.storage import Storage


class State(object):
    def __init__(self, registers=None, memory=None, storage=None, environment=None, return_data=None, reverted=False,
                 stopped=False, destructed=False, invalid=False):
        if registers is None:
            registers = Registers()
        if memory is None:
            memory = Memory()
        if storage is None:
            storage = Storage()
        if environment is None:
            environment = Environment()
        self._registers = registers
        self._memory = memory
        self._storage = storage
        self._environment = environment
        self._return_data = return_data
        self._reverted = reverted
        self._stopped = stopped
        self._destructed = destructed
        self._invalid = invalid

    @property
    def registers(self):
        return self._registers

    @property
    def memory(self):
        return self._memory

    @property
    def storage(self):
        return self._storage

    @property
    def environment(self):
        return self._environment

    @property
    def return_data(self):
        return self._return_data

    @return_data.setter
    def return_data(self, value):
        self._return_data = value

    @property
    def reverted(self):
        return self._reverted

    @reverted.setter
    def reverted(self, value):
        assert (isinstance(value, bool))

        self._reverted = value

    @property
    def stopped(self):
        return self._stopped

    @stopped.setter
    def stopped(self, value):
        assert (isinstance(value, bool))

        self._stopped = value

    @property
    def destructed(self):
        return self._destructed

    @destructed.setter
    def destructed(self, value):
        assert (isinstance(value, bool))

        self._destructed = value

    @property
    def invalid(self):
        return self._invalid

    @invalid.setter
    def invalid(self, value):
        assert (isinstance(value, bool))

        self._invalid = value

    def __copy__(self):
        new_registers = copy(self._registers)
        new_memory = copy(self._memory)
        new_storage = copy(self._storage)
        return State(new_registers, new_memory, new_storage, self._environment, self._return_data, self._reverted,
                     self._stopped, self._destructed, self._invalid)

    def __str__(self):
        return f"Return data: {self._return_data}\nReverted: {self._reverted}\nStopped: {self.stopped}\nDestructed: {self._destructed}\nInvalid: {self._invalid}"
