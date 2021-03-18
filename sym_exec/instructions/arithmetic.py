# https://ethervm.io/#opcodes
import logging

from z3 import simplify, URem, BitVecVal, SRem, BitVec, UDiv, LShR

from rattle import SSAInstruction
from sym_exec.state import State
from sym_exec.utils import get_argument_value, is_all_concrete, CEILING_256_VALUE, WORD_SIZE, to_signed, \
    to_unsigned, is_concrete, is_symbolic

logger = logging.getLogger(__name__)


def inst_stop(instruction: SSAInstruction, state: State):
    state.stopped = True


def inst_add(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 2:
        logger.error(f"ADD instruction needs 2 arguments but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("ADD needs return value")
        raise Exception

    registers = state.registers
    a, b = get_argument_value(args, 0, registers), get_argument_value(args, 1, registers)

    expr = (a + b) % CEILING_256_VALUE
    expr = simplify(expr) if is_symbolic(expr) else expr
    registers.set(rv.value, expr)


def inst_mul(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 2:
        logger.error(f"MUL instruction needs 2 arguments but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("MUL needs return value")
        raise Exception

    registers = state.registers
    a, b = get_argument_value(args, 0, registers), get_argument_value(args, 1, registers)

    expr = (a * b) % CEILING_256_VALUE
    expr = simplify(expr) if is_symbolic(expr) else expr
    registers.set(rv.value, expr)


def inst_sub(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 2:
        logger.error(f"SUB instruction needs 2 arguments but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("SUB needs return value")
        raise Exception

    registers = state.registers
    a, b = get_argument_value(args, 0, registers), get_argument_value(args, 1, registers)

    expr = (a - b) % CEILING_256_VALUE
    expr = simplify(expr) if is_symbolic(expr) else expr
    registers.set(rv.value, expr)


def inst_div(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 2:
        logger.error(f"DIV instruction needs 2 arguments but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("DIV needs return value")
        raise Exception

    registers = state.registers
    a, b = get_argument_value(args, 0, registers), get_argument_value(args, 1, registers)

    if b == 0:
        expr = 0
    else:
        if is_all_concrete(a, b):
            expr = a // b
        else:
            expr = simplify(UDiv(a, b))
    registers.set(rv.value, expr)


def inst_sdiv(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 2:
        logger.error(f"SDIV instruction needs 2 arguments but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("SDIV needs return value")
        raise Exception

    registers = state.registers
    a, b = get_argument_value(args, 0, registers), get_argument_value(args, 1, registers)

    if b == 0:
        expr = 0
    else:
        if is_all_concrete(a, b):
            a = to_signed(a)
            b = to_signed(b)
            sign = -1 if a * b < 0 else 1
            expr = to_unsigned((abs(a) // abs(b)) * sign)
        else:
            expr = simplify(a / b)
    registers.set(rv.value, expr)


def inst_mod(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 2:
        logger.error(f"MOD instruction needs 2 arguments but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("MOD needs return value")
        raise Exception

    registers = state.registers
    a, b = get_argument_value(args, 0, registers), get_argument_value(args, 1, registers)

    if b == 0:
        expr = 0
    else:
        if is_all_concrete(a, b):
            expr = a % b
        else:
            expr = simplify(URem(a, b))
    registers.set(rv.value, expr)


def inst_smod(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 2:
        logger.error(f"SMOD instruction needs 2 arguments but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("SMOD needs return value")
        raise Exception

    registers = state.registers
    a, b = get_argument_value(args, 0, registers), get_argument_value(args, 1, registers)

    if b == 0:
        expr = 0
    else:
        if is_all_concrete(a, b):
            a = to_signed(a)
            b = to_signed(b)
            sign = -1 if a < 0 else 1
            expr = to_unsigned((abs(a) % abs(b)) * sign)
        else:
            expr = simplify(SRem(a, b))
    registers.set(rv.value, expr)


def inst_addmod(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 3:
        logger.error(f"ADDMOD instruction needs 3 arguments but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("ADDMOD needs return value")
        raise Exception

    registers = state.registers
    a, b, n = get_argument_value(args, 0, registers), get_argument_value(args, 1, registers), \
              get_argument_value(args, 2, registers)

    if n == 0:
        expr = 0
    else:
        if is_concrete(n):
            n = BitVecVal(n, WORD_SIZE)
        expr = simplify(URem(URem(a, n) + URem(b, n), n))
    registers.set(rv.value, expr)


def inst_mulmod(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 3:
        logger.error(f"MULMOD instruction needs 3 arguments but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("MULMOD needs return value")
        raise Exception

    registers = state.registers
    a, b, n = get_argument_value(args, 0, registers), get_argument_value(args, 1, registers), \
              get_argument_value(args, 2, registers)

    if n == 0:
        expr = 0
    else:
        if is_concrete(n):
            n = BitVecVal(n, WORD_SIZE)
        expr = simplify(URem(URem(a, n) * URem(b, n), n))
    registers.set(rv.value, expr)


def inst_exp(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 2:
        logger.error(f"EXP instruction needs 2 arguments but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("EXP needs return value")
        raise Exception

    registers = state.registers
    a, b = get_argument_value(args, 0, registers), get_argument_value(args, 1, registers),

    rv = rv.value
    if is_all_concrete(a, b):
        expr = pow(a, b, CEILING_256_VALUE)
    else:
        expr = simplify(BitVec(str(rv), WORD_SIZE))
    registers.set(rv, expr)


def inst_signextend(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 2:
        logger.error(f"SIGNEXTEND needs 2 arguments but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("SIGNEXTEND needs return value")
        raise Exception

    registers = state.registers
    a, b = get_argument_value(args, 0, registers), get_argument_value(args, 1, registers)

    rv = rv.value
    if is_all_concrete(a, b):
        if a <= 31:
            testbit = a * 8 + 7
            signbit = (1 << testbit)
            if b & signbit:
                expr = b | (CEILING_256_VALUE - signbit)
            else:
                expr = b & (signbit - 1)
        else:
            expr = b
    else:
        expr = simplify(BitVec(str(rv), WORD_SIZE))
    registers.set(rv, expr)


def inst_shl(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 2:
        logger.error(f"SHL instruction needs 2 arguments but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("SHL instruction needs return value")
        raise Exception

    registers = state.registers
    shift, value = get_argument_value(args, 0, registers), get_argument_value(args, 1, registers)

    expr = (value << shift) % CEILING_256_VALUE
    expr = simplify(expr) if is_symbolic(expr) else expr
    registers.set(rv.value, expr)


def inst_shr(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 2:
        logger.error(f"SHR instruction needs 2 arguments but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("SHR instruction needs return value")
        raise Exception

    registers = state.registers
    shift, value = get_argument_value(args, 0, registers), get_argument_value(args, 1, registers)

    if is_all_concrete(shift, value):
        expr = value >> shift
    else:
        expr = simplify(LShR(value, shift))
    registers.set(rv.value, expr)


def inst_sar(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 2:
        logger.error(f"SAR instruction needs 2 arguments but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("SAR instruction needs return value")
        raise Exception

    registers = state.registers
    shift, value = get_argument_value(args, 0, registers), get_argument_value(args, 1, registers)

    if is_all_concrete(shift, value):
        value = to_signed(value)
        if shift >= WORD_SIZE:
            expr = 0 if value >= 0 else (CEILING_256_VALUE - 1)
        else:
            expr = to_unsigned(value >> shift)
    else:
        expr = simplify(value >> shift)
    registers.set(rv.value, expr)
