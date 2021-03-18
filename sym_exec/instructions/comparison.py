# https://ethervm.io/#opcodes
import logging

from z3 import If, ULT, BitVecVal, UGT, Concat, Extract, BitVec

from rattle import SSAInstruction
from sym_exec.state import State
from sym_exec.utils import get_argument_value, is_all_concrete, is_concrete, to_signed, WORD_SIZE, MAX_UVALUE, \
    is_symbolic

logger = logging.getLogger(__name__)


def inst_lt(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 2:
        logger.error(f"LT instruction needs 2 arguments but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("LT instruction needs return value")
        raise Exception

    registers = state.registers
    a, b = get_argument_value(args, 0, registers), get_argument_value(args, 1, registers)

    if is_all_concrete(a, b):
        if a < b:
            expr = 1
        else:
            expr = 0
    else:
        expr = If(ULT(a, b), BitVecVal(1, WORD_SIZE), BitVecVal(0, WORD_SIZE))
    registers.set(rv.value, expr)


def inst_gt(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 2:
        logger.error(f"GT instruction needs 2 arguments but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("GT instruction needs return value")
        raise Exception

    registers = state.registers
    a, b = get_argument_value(args, 0, registers), get_argument_value(args, 1, registers)

    if is_all_concrete(a, b):
        if a > b:
            expr = 1
        else:
            expr = 0
    else:
        expr = If(UGT(a, b), BitVecVal(1, WORD_SIZE), BitVecVal(0, WORD_SIZE))
    registers.set(rv.value, expr)


def inst_slt(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 2:
        logger.error(f"SLT instruction needs 2 arguments but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("SLT instruction needs return value")
        raise Exception

    registers = state.registers
    a, b = get_argument_value(args, 0, registers), get_argument_value(args, 1, registers)

    if is_all_concrete(a, b):
        a = to_signed(a)
        b = to_signed(b)
        if a < b:
            expr = 1
        else:
            expr = 0
    else:
        expr = If(a < b, BitVecVal(1, WORD_SIZE), BitVecVal(0, WORD_SIZE))
    registers.set(rv.value, expr)


def inst_sgt(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 2:
        logger.error(f"SGT instruction needs 2 arguments but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("SGT instruction needs return value")
        raise Exception

    registers = state.registers
    a, b = get_argument_value(args, 0, registers), get_argument_value(args, 1, registers)

    if is_all_concrete(a, b):
        a = to_signed(a)
        b = to_signed(b)
        if a > b:
            expr = 1
        else:
            expr = 0
    else:
        expr = If(a > b, BitVecVal(1, WORD_SIZE), BitVecVal(0, WORD_SIZE))
    registers.set(rv.value, expr)


def inst_eq(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 2:
        logger.error(f"EQ instruction needs 2 arguments but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("EQ instruction needs return value")
        raise Exception

    registers = state.registers
    a, b = get_argument_value(args, 0, registers), get_argument_value(args, 1, registers)

    if is_all_concrete(a, b):
        if a == b:
            expr = 1
        else:
            expr = 0
    else:
        expr = If(a == b, BitVecVal(1, WORD_SIZE), BitVecVal(0, WORD_SIZE))
    registers.set(rv.value, expr)


def inst_iszero(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 1:
        logger.error(f"EQ instruction needs 1 arguments but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("EQ instruction needs return value")
        raise Exception

    registers = state.registers
    a = get_argument_value(args, 0, registers)

    if is_concrete(a):
        if a == 0:
            expr = 1
        else:
            expr = 0
    else:
        expr = If(a == 0, BitVecVal(1, WORD_SIZE), BitVecVal(0, WORD_SIZE))
    registers.set(rv.value, expr)


def inst_and(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 2:
        logger.error(f"AND instruction needs 2 arguments but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("AND instruction needs return value")
        raise Exception

    registers = state.registers
    a, b = get_argument_value(args, 0, registers), get_argument_value(args, 1, registers)

    expr = a & b
    registers.set(rv.value, expr)


def inst_or(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 2:
        logger.error(f"OR instruction needs 2 arguments but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("OR instruction needs return value")
        raise Exception

    registers = state.registers
    a, b = get_argument_value(args, 0, registers), get_argument_value(args, 1, registers)

    expr = a | b
    registers.set(rv.value, expr)


def inst_xor(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 2:
        logger.error(f"XOR instruction needs 2 arguments but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("XOR instruction needs return value")
        raise Exception

    registers = state.registers
    a, b = get_argument_value(args, 0, registers), get_argument_value(args, 1, registers)

    expr = a ^ b
    registers.set(rv.value, expr)


def inst_not(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 1:
        logger.error(f"NOT instruction needs 1 arguments but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("NOT instruction needs return value")
        raise Exception

    registers = state.registers
    a = get_argument_value(args, 0, registers)

    expr = MAX_UVALUE - a
    registers.set(rv.value, expr)


def inst_byte(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 2:
        logger.error(f"BYTE instruction needs 2 arguments but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("BYTE instruction needs return value")
        raise Exception

    registers = state.registers
    i, x = get_argument_value(args, 0, registers), get_argument_value(args, 1, registers)

    rv = rv.value
    if is_symbolic(i):
        expr = BitVec(str(rv), WORD_SIZE)
    else:
        if i >= 32:
            expr = 0
        else:
            if is_concrete(x):
                expr = (x >> (248 - (i * 8))) & 0xff
            else:
                low = 248 - (i * 8)
                expr = Concat(BitVecVal(0, WORD_SIZE - 8), Extract(low + 7, low, x))

    registers.set(rv, expr)
