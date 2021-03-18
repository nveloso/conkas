# https://ethervm.io/#opcodes
import logging

from z3 import BitVec

from rattle import SSAInstruction
from sym_exec.state import State
from sym_exec.utils import get_argument_value, is_symbolic, WORD_SIZE

logger = logging.getLogger(__name__)


def inst_blockhash(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 1:
        logger.error(f"BLOCKHASH instruction needs 1 arguments but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("BLOCKHASH instruction needs return value")
        raise Exception

    block_number = get_argument_value(args, 0, state.registers)
    if is_symbolic(block_number):
        bv_name = f'block_number_sym_{block_number}'
    else:
        bv_name = f'block_number_{block_number}'

    rv = rv.value
    bv = BitVec(bv_name, WORD_SIZE)
    state.registers.set(rv, bv)


def inst_coinbase(instruction: SSAInstruction, state: State):
    rv = instruction.return_value
    if rv is None:
        logger.error("COINBASE instruction needs return value")
        raise Exception

    rv = rv.value
    bv = BitVec('coinbase', WORD_SIZE)
    state.registers.set(rv, bv)


def inst_timestamp(instruction: SSAInstruction, state: State):
    rv = instruction.return_value
    if rv is None:
        logger.error("TIMESTAMP instruction needs return value")
        raise Exception

    rv = rv.value
    bv = BitVec('timestamp', WORD_SIZE)
    state.registers.set(rv, bv)


def inst_number(instruction: SSAInstruction, state: State):
    rv = instruction.return_value
    if rv is None:
        logger.error("NUMBER instruction needs return value")
        raise Exception

    rv = rv.value
    bv = BitVec('number', WORD_SIZE)
    state.registers.set(rv, bv)


def inst_difficulty(instruction: SSAInstruction, state: State):
    rv = instruction.return_value
    if rv is None:
        logger.error("DIFFICULTY instruction needs return value")
        raise Exception

    rv = rv.value
    bv = BitVec('difficulty', WORD_SIZE)
    state.registers.set(rv, bv)


def inst_gaslimit(instruction: SSAInstruction, state: State):
    rv = instruction.return_value
    if rv is None:
        logger.error("GASLIMIT instruction needs return value")
        raise Exception

    rv = rv.value
    bv = BitVec('gaslimit', WORD_SIZE)
    state.registers.set(rv, bv)


def inst_chainid(instruction: SSAInstruction, state: State):
    rv = instruction.return_value
    if rv is None:
        logger.error("CHAINID instruction needs return value")
        raise Exception

    rv = rv.value
    bv = BitVec('chainid', WORD_SIZE)
    state.registers.set(rv, bv)
