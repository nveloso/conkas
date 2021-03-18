import logging

from rattle import ConditionalInternalCall, InternalCall, SSAInstruction
from sym_exec.state import State
from sym_exec.utils import get_argument_value, is_concrete

logger = logging.getLogger(__name__)


def inst_condicall(instruction: ConditionalInternalCall, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 1:
        logger.error(f"CONDICALL instruction needs 1 arguments but {args_len} was given")
        raise Exception

    target = instruction.target
    condition = get_argument_value(args, 0, state.registers)

    jump_to = target.blockmap.get(target.offset, None)
    if jump_to is None:
        logger.warning("Could not find the offset to jump in CONDICALL instruction")
        return

    fallthrough_block = instruction.parent_block.fallthrough_edge
    if fallthrough_block is None:
        logger.warning("Could not find the fallthrough block to jump")
        return

    if is_concrete(condition):
        if condition:
            return [(jump_to, None)]
        return [(fallthrough_block, None)]

    return [(fallthrough_block, condition == 0), (jump_to, condition != 0)]


def inst_icall(instruction: InternalCall, state):
    pb = instruction.parent_block
    condition = None
    try:
        possible_jumpi = pb.insns[-2]
        if possible_jumpi.insn.name == 'JUMPI':
            condition = get_argument_value(possible_jumpi.arguments, 1, state.registers) == 0
    except IndexError:
        pass
    target = instruction.target
    offset = target.offset
    return [(target.blockmap.get(offset), condition)]


def inst_phi(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args.sort(key=lambda stack_value: stack_value.value, reverse=True)
    args_len = len(args)
    if args_len == 0:
        logger.error(f"PHI instruction need arguments but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("PHI instruction needs return value")
        raise Exception

    rv = rv.value
    registers = state.registers

    val = None
    for i in range(args_len):
        temp = get_argument_value(args, i, registers)
        if temp is not None:
            val = temp
            break

    if val is None:
        logger.warning("Could not found any value for PHI instruction arguments")
        return

    registers.set(rv, val)
