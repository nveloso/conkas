# https://ethervm.io/#opcodes
import logging

from z3 import BitVec

from rattle import SSAInstruction
from sym_exec.state import State
from sym_exec.utils import get_argument_value, WORD_SIZE, is_symbolic, is_concrete

logger = logging.getLogger(__name__)


def inst_create(instruction: SSAInstruction, state: State):
    args_len = len(instruction.arguments)
    if args_len != 3:
        logger.error(f"CREATE instruction needs 3 arguments but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("CREATE instruction needs return value")
        raise Exception

    rv = rv.value
    state.registers.set(rv, BitVec(str(rv), WORD_SIZE))


def __call(ret_offset, ret_length, instruction: SSAInstruction, state: State):
    rv = instruction.return_value.value
    if is_symbolic(ret_offset) or is_symbolic(ret_length):
        logger.warning("RET_OFFSET or RET_LENGTH is symbolic in CREATE, CALLCODE or DELEGATECALL instruction")
    else:
        mem = state.memory
        mem.extend(ret_offset, ret_length)
        if ret_length > 0:
            bv = BitVec('ret_code_' + str(rv), ret_length * 8)
            mem.store(ret_offset, bv, ret_length)

    state.registers.set(rv, BitVec(str(rv), WORD_SIZE))


def inst_call(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 7:
        logger.error(f"CALL instruction needs 7 arguments but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("CALL instruction needs return value")
        raise Exception

    registers = state.registers
    ret_offset, ret_length = get_argument_value(args, 5, registers), get_argument_value(args, 6, registers)

    __call(ret_offset, ret_length, instruction, state)


def inst_callcode(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 7:
        logger.error(f"CALLCODE instruction needs 7 arguments but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("CALLCODE instruction needs return value")
        raise Exception

    registers = state.registers
    ret_offset, ret_length = get_argument_value(args, 5, registers), get_argument_value(args, 6, registers)

    __call(ret_offset, ret_length, instruction, state)


def inst_return(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 2:
        logger.error(f"RETURN instruction needs 2 argument but {args_len} was given")
        raise Exception

    registers = state.registers
    offset, length = get_argument_value(args, 0, registers), get_argument_value(args, 1, registers)

    if is_symbolic(length):
        logger.warning("RETURN instruction has symbolic length")
        state.return_data = BitVec('ret_data', WORD_SIZE)
        return

    mem = state.memory
    if is_concrete(offset):
        mem.extend(offset, length)

    return_data = mem.load(offset, length)
    state.return_data = return_data


def inst_delegatecall(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 6:
        logger.error(f"DELEGATECALL instruction needs 6 arguments but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("DELEGATECALL instruction needs return value")
        raise Exception

    registers = state.registers
    ret_offset, ret_length = get_argument_value(args, 4, registers), get_argument_value(args, 5, registers)

    __call(ret_offset, ret_length, instruction, state)


# TODO: test
def inst_create2(instruction: SSAInstruction, state: State):
    args_len = len(instruction.arguments)
    if args_len != 4:
        logger.error(f"CREATE2 instruction needs 4 arguments but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("CREATE2 instruction needs return value")
        raise Exception

    rv = rv.value
    state.registers.set(rv, BitVec(str(rv), WORD_SIZE))


def inst_staticcall(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 6:
        logger.error(f"STATICCALL instruction needs 6 arguments but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("STATICCALL instruction needs return value")
        raise Exception

    registers = state.registers
    ret_offset, ret_length = get_argument_value(args, 4, registers), get_argument_value(args, 5, registers)

    __call(ret_offset, ret_length, instruction, state)


def inst_revert(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 2:
        logger.error(f"REVERT instruction needs 2 arguments but {args_len} was given")
        raise Exception

    registers = state.registers
    offset, length = get_argument_value(args, 0, registers), get_argument_value(args, 1, registers)

    state.reverted = True

    if is_symbolic(length):
        logger.warning("REVERT instruction has symbolic length")
        state.return_data = BitVec('rev_data', WORD_SIZE)
        return

    mem = state.memory
    if is_concrete(offset):
        mem.extend(offset, length)

    return_data = mem.load(offset, length)
    state.return_data = return_data


def inst_invalid(instruction: SSAInstruction, state: State):
    state.invalid = True


def inst_selfdestruct(instruction: SSAInstruction, state: State):
    args_len = len(instruction.arguments)
    if args_len != 1:
        logger.error(f"SELFDESTRUCT instruction needs 1 arguments but {args_len} was given")
        raise Exception

    state.destructed = True
