# https://ethervm.io/#opcodes
import logging

from rattle import SSAInstruction
from sym_exec.state import State
from sym_exec.utils import get_argument_value, is_symbolic

logger = logging.getLogger(__name__)


def inst_push(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 1:
        logger.error(f"PUSH instruction needs 1 arguments but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("PUSH instruction needs return value")
        raise Exception

    registers = state.registers
    value = get_argument_value(args, 0, registers)

    if is_symbolic(value):
        logger.error("PUSH instruction needs a concrete argument")
        raise Exception

    registers.set(rv.value, value)
