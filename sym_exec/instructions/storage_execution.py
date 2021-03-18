# https://ethervm.io/#opcodes
import logging

from z3 import BitVec

from rattle import SSAInstruction
from sym_exec.state import State
from sym_exec.utils import get_argument_value, is_concrete, WORD_SIZE, is_symbolic

logger = logging.getLogger(__name__)


def inst_mload(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 1:
        logger.error(f"MLOAD instruction needs 1 argument but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("MLOAD instruction needs return value")
        raise Exception

    registers = state.registers
    offset = get_argument_value(args, 0, registers)

    mem = state.memory
    if is_concrete(offset):
        mem.extend(offset, 32)

    value = mem.load(offset)
    registers.set(rv.value, value)


def inst_mstore(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 2:
        logger.error(f"MSTORE instruction needs 2 argument but {args_len} was given")
        raise Exception

    registers = state.registers
    offset, value = get_argument_value(args, 0, registers), get_argument_value(args, 1, registers)

    mem = state.memory
    if is_concrete(offset):
        mem.extend(offset, 32)

    mem.store(offset, value)


def inst_mstore8(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 2:
        logger.error(f"MSTORE8 instruction needs 2 argument but {args_len} was given")
        raise Exception

    registers = state.registers
    offset, value = get_argument_value(args, 0, registers), get_argument_value(args, 1, registers)

    mem = state.memory
    if is_concrete(offset):
        mem.extend(offset, 1)

    mem.store(offset, value, 1)


def inst_sload(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 1:
        logger.error(f"SLOAD instruction needs 1 argument but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("SLOAD instruction needs return value")
        raise Exception

    registers = state.registers
    key = get_argument_value(args, 0, registers)

    storage = state.storage
    value = storage.get(key)

    if value is None:
        if is_symbolic(key):
            bv_name = f"storage,{args[0].value},sym"
        else:
            bv_name = f"storage,{str(key)},conc"
        value = BitVec(bv_name, WORD_SIZE)
        storage.set(key, value)

    registers.set(rv.value, value)


def inst_sstore(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 2:
        logger.error(f"SSTORE instruction needs 2 argument but {args_len} was given")
        raise Exception

    registers = state.registers
    key, value = get_argument_value(args, 0, registers), get_argument_value(args, 1, registers)

    state.storage.set(key, value)


def __get_true_path_block(parent_block, destination):
    if parent_block is None:
        return

    jumps = parent_block.jump_edges
    if jumps is None:
        return

    possible_jumps = list(filter(lambda x: x.offset == destination, jumps))
    if len(possible_jumps) != 1:
        logger.warning("Cannot find a block to jump")
        return
    return possible_jumps[0]


def __get_false_path_block(parent_block):
    if parent_block is None:
        return

    fallthrough_block = parent_block.fallthrough_edge
    if fallthrough_block is not None:
        return fallthrough_block


def inst_jump(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 1:
        logger.error(f"JUMP instruction needs 1 argument but {args_len} was given")
        raise Exception

    registers = state.registers
    destination = get_argument_value(args, 0, registers)

    if is_symbolic(destination):
        logger.warning("Destination argument is symbolic in JUMP instruction.")
        return

    pb = instruction.parent_block
    fallthrough_block = __get_false_path_block(pb)
    if fallthrough_block is not None and fallthrough_block.offset == destination:
        logger.warning("JUMP should not have fallthrough block. Something is wrong...")
        return [(fallthrough_block, None)]

    possible_jump = __get_true_path_block(pb, destination)
    if possible_jump is not None:
        return [(possible_jump, None)]


def inst_jumpi(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 2:
        logger.error(f"JUMPI instruction needs 2 argument but {args_len} was given")
        raise Exception

    registers = state.registers
    destination, condition = get_argument_value(args, 0, registers), get_argument_value(args, 1, registers)

    if is_symbolic(destination):
        logger.warning("JUMPI needs destination to be concrete.")
        return

    pb = instruction.parent_block
    if is_concrete(condition):
        if condition:
            return [(__get_true_path_block(pb, destination), None)]
        return [(__get_false_path_block(pb), None)]

    false_block = __get_false_path_block(pb)
    true_block = __get_true_path_block(pb, destination)

    possible_jumps = []
    if false_block is not None:
        possible_jumps.append((false_block, condition == 0))

    if true_block is not None:
        possible_jumps.append((true_block, condition != 0))

    return possible_jumps


def inst_pc(instruction: SSAInstruction, state: State):
    rv = instruction.return_value
    if rv is None:
        logger.error("PC instruction needs return value")
        raise Exception

    state.registers.set(rv.value, instruction.offset)


def inst_msize(instruction: SSAInstruction, state: State):
    rv = instruction.return_value
    if rv is None:
        logger.error("MSIZE instruction needs return value")
        raise Exception

    state.registers.set(rv.value, state.memory.size)


def inst_gas(instruction: SSAInstruction, state: State):
    rv = instruction.return_value
    if rv is None:
        logger.error("GAS instruction needs return value")
        raise Exception

    rv = rv.value
    gas = BitVec(str(rv), WORD_SIZE)
    state.registers.set(rv, gas)


def inst_jumpdest(instruction: SSAInstruction, state: State):
    logger.error("JUMPDEST instruction should not be reached")
    raise Exception
