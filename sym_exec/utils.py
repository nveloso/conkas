from z3 import ExprRef

from rattle import ConcreteStackValue

CEILING_256_VALUE = 0x10000000000000000000000000000000000000000000000000000000000000000
MAX_UVALUE = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
MAX_SVALUE = 0x7fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
WORD_SIZE = 256


def is_symbolic(value):
    return isinstance(value, ExprRef)


def is_concrete(value):
    return isinstance(value, int)


def is_all_concrete(*values):
    for value in values:
        if is_symbolic(value):
            return False
    return True


def to_signed(value):
    if value <= MAX_SVALUE:
        return value
    else:
        return value - CEILING_256_VALUE


def to_unsigned(value):
    if value < 0:
        return value + CEILING_256_VALUE
    else:
        return value


def get_argument_value(arguments, idx, registers):
    arg = arguments[idx]
    if isinstance(arg, ConcreteStackValue):
        return arg.concrete_value

    return registers.get(arg.value)


def ceil32(value):
    remainder = value % 32
    if remainder == 0:
        return value
    else:
        return value + 32 - remainder
