# https://ethervm.io/#opcodes
import logging

from Crypto.Hash import keccak
from z3 import BitVec, simplify

from rattle import SSAInstruction
from sym_exec.state import State
from sym_exec.utils import get_argument_value, is_all_concrete, WORD_SIZE, is_symbolic

logger = logging.getLogger(__name__)

EMPTY_KECCAK_256 = 0xc5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470


def inst_sha3(instruction: SSAInstruction, state: State):
    args = instruction.arguments
    args_len = len(args)
    if args_len != 2:
        logger.error(f"SHA3 instruction needs 2 arguments but {args_len} was given")
        raise Exception

    rv = instruction.return_value
    if rv is None:
        logger.error("SHA3 instruction needs return value")
        raise Exception

    registers = state.registers
    offset, length = get_argument_value(args, 0, registers), get_argument_value(args, 1, registers)

    rv = rv.value
    if is_all_concrete(offset, length):
        if length == 0:
            expr = EMPTY_KECCAK_256
        else:
            mem = state.memory
            mem.extend(offset, length)
            val = mem.load(offset, length, read_as_bytes=True)
            if is_symbolic(val):
                expr = simplify(val).hash()
            else:
                keccak_hash = keccak.new(data=val, digest_bits=256)
                expr = int(keccak_hash.hexdigest(), 16)
    else:
        expr = BitVec(str(rv), WORD_SIZE)
    registers.set(rv, expr)
