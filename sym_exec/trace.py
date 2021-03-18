import logging
from copy import copy

from z3 import BoolRef

from rattle import SSABasicBlock
from sym_exec.analyzed_block import AnalyzedBlock
from sym_exec.environment import Environment
from sym_exec.state import State

logger = logging.getLogger(__name__)


class Trace(object):
    def __init__(self, block_to_analyse=None, analyzed_blocks=None, state=None, environment=None, depth=0,
                 constraints=None, current_constraint=None):
        if analyzed_blocks is None:
            analyzed_blocks = []
        if constraints is None:
            constraints = []

        self._block_to_analyse: SSABasicBlock = block_to_analyse
        self._analyzed_blocks: [AnalyzedBlock] = analyzed_blocks
        if environment is None:
            logger.info("Running without any environment")
            environment = Environment()
        if state is None:
            state = State(environment=environment)
        self._state = state
        self._environment = environment
        self._depth = depth
        self._constraints: [] = constraints
        self._current_constraint = current_constraint

    @property
    def block_to_analyse(self):
        return self._block_to_analyse

    @block_to_analyse.setter
    def block_to_analyse(self, value):
        assert isinstance(value, SSABasicBlock)

        self._block_to_analyse = value

    @block_to_analyse.deleter
    def block_to_analyse(self):
        del self._block_to_analyse

    @property
    def analyzed_blocks(self):
        return self._analyzed_blocks

    @property
    def state(self):
        return self._state

    @property
    def depth(self):
        return self._depth

    @depth.setter
    def depth(self, value):
        assert isinstance(value, int)

        self._depth = value

    @property
    def constraints(self):
        return self._constraints

    @property
    def current_constraint(self):
        return self._current_constraint

    @current_constraint.setter
    def current_constraint(self, constraint):
        if constraint is None:
            self._current_constraint = None
            return

        assert isinstance(constraint, bool) or isinstance(constraint, BoolRef)
        self._current_constraint = constraint
        self._constraints.append(constraint)

    @current_constraint.deleter
    def current_constraint(self):
        del self._current_constraint

    def add_analysed_block(self, analyzed_block):
        self._analyzed_blocks.append(analyzed_block)
        self._block_to_analyse = None

    def __copy__(self):
        new_state = copy(self._state)
        return Trace(self._block_to_analyse, self._analyzed_blocks.copy(), new_state, self._environment, self._depth,
                     self._constraints.copy(), self._current_constraint)
