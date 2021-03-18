# https://ethervm.io/#opcodes
import logging

from z3 import BitVec

from rattle import SSAInstruction
from sym_exec.state import State
from sym_exec.utils import get_argument_value, is_all_concrete, WORD_SIZE, is_symbolic

logger = logging.getLogger(__name__)


def inst_address(instruction: SSAInstruction, state: State):
    rv = instruction.return_value
    if rv is None:
        logger.error("ADDRESS instruction needs return value")
        raise Exception

    rv = rv.value
    address = BitVec('address', WORD_SIZE)
    state.registers.set(rv, address)


def inst_balance(instruction: SSAInstruction, state: State):
    args_len = len(instruction.arguments)
    if args_len != 1:
        logger.error(f"BALANCE instruction needs 1 arguments but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("BALANCE instruction needs return value")
        raise Exception

    rv = rv.value
    balance = BitVec(str(rv), WORD_SIZE)
    state.registers.set(rv, balance)


def inst_selfbalance(instruction: SSAInstruction, state: State):
    rv = instruction.return_value
    if rv is None:
        logger.error("SELFBALANCE instruction needs return value")
        raise Exception

    rv = rv.value
    selfbalance = BitVec(str(rv), WORD_SIZE)
    state.registers.set(rv, selfbalance)


def inst_origin(instruction: SSAInstruction, state: State):
    rv = instruction.return_value
    if rv is None:
        logger.error("ORIGIN instruction needs return value")
        raise Exception

    rv = rv.value
    origin = BitVec('origin', WORD_SIZE)
    state.registers.set(rv, origin)


def inst_caller(instruction: SSAInstruction, state: State):
    rv = instruction.return_value
    if rv is None:
        logger.error("CALLER instruction needs return value")
        raise Exception

    rv = rv.value
    caller = BitVec('caller', WORD_SIZE)
    state.registers.set(rv, caller)


def inst_callvalue(instruction: SSAInstruction, state: State):
    rv = instruction.return_value
    if rv is None:
        logger.error("CALLVALUE instruction needs return value")
        raise Exception

    rv = rv.value
    callvalue = BitVec('callvalue', WORD_SIZE)
    state.registers.set(rv, callvalue)


def inst_calldataload(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 1:
        logger.error(f"CALLDATALOAD instruction needs 1 arguments but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("CALLDATALOAD instruction needs return value")
        raise Exception

    i = get_argument_value(args, 0, state.registers)

    if is_symbolic(i):
        bv_name = f'calldataload_sym_{i}'
    else:
        bv_name = f'calldataload_{i}'

    rv = rv.value
    res = BitVec(bv_name, WORD_SIZE)
    state.registers.set(rv, res)


def inst_calldatasize(instruction: SSAInstruction, state: State):
    rv = instruction.return_value
    if rv is None:
        logger.error("CALLDATASIZE instruction needs return value")
        raise Exception

    rv = rv.value
    calldatasize = BitVec('calldatasize', WORD_SIZE)
    state.registers.set(rv, calldatasize)


def inst_calldatacopy(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 3:
        logger.error(f"CALLDATACOPY instruction needs 3 arguments but {args_len} was given")
        raise Exception

    registers = state.registers
    dest_offset, length = get_argument_value(args, 0, registers), get_argument_value(args, 2, registers)

    if not is_all_concrete(dest_offset, length):
        logger.warning("CALLDATACOPY needs concrete values")
        return

    mem = state.memory
    mem.extend(dest_offset, length)
    bv = BitVec(str(hash(instruction)), length * 8)
    mem.store(dest_offset, bv, size=length)


def inst_codesize(instruction: SSAInstruction, state: State):
    rv = instruction.return_value
    if rv is None:
        logger.error("CODESIZE instruction needs return value")
        raise Exception

    rv = rv.value
    code_size = len(state.environment.contract_code) // 2
    state.registers.set(rv, code_size)


def inst_codecopy(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 3:
        logger.error(f"CODECOPY instruction needs 3 arguments but {args_len} was given")
        raise Exception

    registers = state.registers
    dest_offset, offset, length = get_argument_value(args, 0, registers), get_argument_value(args, 1, registers), \
                                  get_argument_value(args, 2, registers)

    if is_symbolic(dest_offset):
        logger.warning("Symbolic memory index in CODECOPY instruction")
        return

    mem = state.memory
    if is_symbolic(length):
        logger.warning("Symbolic length in CODECOPY instruction")
        mem.extend(dest_offset, 1)
        mem.store(dest_offset, BitVec(str(hash(instruction)), 8), 1)
        return

    if is_symbolic(offset):
        mem.extend(dest_offset, length)
        mem.store(dest_offset, BitVec(str(hash(instruction)), length * 8), length)
        return

    mem.extend(dest_offset, length)
    code = state.environment.contract_code
    start_idx = offset * 2
    end_idx = start_idx + (length * 2)
    try:
        code = int(code[start_idx:end_idx].decode('utf-8'), 16)
    except ValueError:
        code = BitVec(str(hash(instruction)), length * 8)
    mem.store(dest_offset, code, length)


def inst_gasprice(instruction: SSAInstruction, state: State):
    rv = instruction.return_value
    if rv is None:
        logger.error("GASPRICE instruction needs return value")
        raise Exception

    rv = rv.value
    bv = BitVec('gasprice', WORD_SIZE)
    state.registers.set(rv, bv)


def inst_extcodesize(instruction: SSAInstruction, state: State):
    args_len = len(instruction.arguments)
    if args_len != 1:
        logger.error(f"EXTCODESIZE instruction needs 1 arguments but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("EXTCODESIZE instruction needs return value")
        raise Exception

    rv = rv.value
    bv = BitVec(str(rv), WORD_SIZE)
    state.registers.set(rv, bv)


def inst_extcodecopy(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 4:
        logger.error(f"EXTCODECOPY instruction needs 4 arguments but {args_len} was given")
        raise Exception

    registers = state.registers
    dest_offset, length = get_argument_value(args, 1, registers), get_argument_value(args, 3, registers)

    if is_symbolic(dest_offset):
        logger.warning("Symbolic memory index in EXTCODECOPY instruction")
        return

    mem = state.memory
    if is_symbolic(length):
        logger.warning("Symbolic length in EXTCODECOPY instruction")
        mem.extend(dest_offset, 1)
        mem.store(dest_offset, BitVec(str(hash(instruction)), 8), 1)
        return

    mem.extend(dest_offset, length)
    mem.store(dest_offset, BitVec(str(hash(instruction)), length * 8), length)


def inst_returndatasize(instruction: SSAInstruction, state: State):
    rv = instruction.return_value
    if rv is None:
        logger.error("RETURNDATASIZE instruction needs return value")
        raise Exception

    rv = rv.value
    bv = BitVec(str(rv), WORD_SIZE)
    state.registers.set(rv, bv)


def inst_returndatacopy(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 3:
        logger.error(f"RETURNDATACOPY instruction needs 3 arguments but {args_len} was given")
        raise Exception

    registers = state.registers
    dest_offset, length = get_argument_value(args, 0, registers), get_argument_value(args, 2, registers)

    if is_symbolic(dest_offset):
        logger.warning("Symbolic memory index in RETURNDATACOPY instruction")
        return

    mem = state.memory
    if is_symbolic(length):
        logger.warning("Symbolic length in RETURNDATACOPY instruction")
        mem.extend(dest_offset, 1)
        mem.store(dest_offset, BitVec(str(hash(instruction)), 8), 1)
        return

    mem.extend(dest_offset, length)
    mem.store(dest_offset, BitVec(str(hash(instruction)), length * 8), length)


def inst_extcodehash(instruction: SSAInstruction, state: State):
    args_len = len(instruction.arguments)
    if args_len != 1:
        logger.error(f"EXTCODEHASH instruction needs 1 arguments but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("EXTCODEHASH instruction needs return value")
        raise Exception

    rv = rv.value
    bv = BitVec(str(rv), WORD_SIZE)
    state.registers.set(rv, bv)
