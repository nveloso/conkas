# https://ethervm.io/#opcodes
import logging

from rattle import SSAInstruction
from sym_exec.state import State
from sym_exec.utils import get_argument_value, is_symbolic

logger = logging.getLogger(__name__)


def __log(state, args):
    registers = state.registers
    offset, length = get_argument_value(args, 0, registers), get_argument_value(args, 1, registers)

    if is_symbolic(offset) or is_symbolic(length):
        return

    state.memory.extend(offset, length)


def inst_log0(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 2:
        logger.error(f"LOG0 instruction needs 2 arguments but {args_len} was given")
        raise Exception

    __log(state, args)


def inst_log1(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(instruction.arguments)
    if args_len != 3:
        logger.error(f"LOG1 instruction needs 3 arguments but {args_len} was given")
        raise Exception

    __log(state, args)


def inst_log2(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(instruction.arguments)
    if args_len != 4:
        logger.error(f"LOG2 instruction needs 4 arguments but {args_len} was given")
        raise Exception

    __log(state, args)


def inst_log3(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(instruction.arguments)
    if args_len != 5:
        logger.error(f"LOG3 instruction needs 5 arguments but {args_len} was given")
        raise Exception

    __log(state, args)


def inst_log4(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(instruction.arguments)
    if args_len != 6:
        logger.error(f"LOG4 instruction needs 6 arguments but {args_len} was given")
        raise Exception

    __log(state, args)
