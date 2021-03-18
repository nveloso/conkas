from rattle import SSABasicBlock


class AnalyzedBlock:
    def __init__(self, block: SSABasicBlock, state=None, constraints: [] = None):
        if constraints is None:
            constraints = []
        self._block: SSABasicBlock = block
        self._state = state
        self._constraints: tuple = tuple(constraints)

    @property
    def block(self):
        return self._block

    @property
    def state(self):
        return self._state

    @property
    def constraints(self):
        return self._constraints

    def __eq__(self, other):
        if not isinstance(other, AnalyzedBlock):
            raise NotImplementedError
        return self._block == other._block and self._state == other._state and self._constraints == other._constraints

    def __hash__(self):
        return hash((self._block, self._state, self._constraints))
