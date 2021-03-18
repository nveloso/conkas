# Analyse arithmetic vulnerabilities
from z3 import Solver, ULT, sat, UGT, BVMulNoOverflow, Not
from z3.z3util import get_vars

from sym_exec.trace import Trace
from sym_exec.utils import get_argument_value, CEILING_256_VALUE, is_concrete, is_all_concrete
from vuln_finder import vulnerability_finder
from vuln_finder.vulnerability import Vulnerability

INTEGER_OVERFLOW_TYPE = 'Integer Overflow'
INTEGER_UNDERFLOW_TYPE = 'Integer Underflow'
ADD = 'ADD'
MUL = 'MUL'
SUB = 'SUB'
EXP = 'EXP'


def __get_solver(timeout=None):
    if timeout is None:
        timeout = vulnerability_finder.Z3_TIMEOUT
    s = Solver()
    s.set('timeout', timeout)
    return s


def __get_value(model, x):
    m = model[get_vars(x)[0]]
    try:
        return m.as_long()
    except AttributeError:
        return m


def __extract_values(model, a, b):
    values = {}
    if is_concrete(a):
        values['a'] = a
    else:
        values['a'] = __get_value(model, a)
    if is_concrete(b):
        values['b'] = b
    else:
        values['b'] = __get_value(model, b)
    return values


def __handle_add_overflow(instruction, analyzed_block, all_constraints):
    args = instruction.arguments
    regs = analyzed_block.state.registers
    a, b = get_argument_value(args, 0, regs), get_argument_value(args, 1, regs)
    c = (a + b) % CEILING_256_VALUE
    if is_concrete(c):
        if c < a:
            model = {
                'a': a,
                'b': b
            }
            return Vulnerability(INTEGER_OVERFLOW_TYPE, analyzed_block, instruction.offset,
                                 instruction.instruction_offset, model)
    else:
        s = __get_solver()
        s.add(all_constraints)
        s.add(ULT(c, a))
        if s.check() == sat:
            return Vulnerability(INTEGER_OVERFLOW_TYPE, analyzed_block, instruction.offset,
                                 instruction.instruction_offset, __extract_values(s.model(), a, b))


def __handle_mul_overflow(instruction, analyzed_block, all_constraints):
    args = instruction.arguments
    regs = analyzed_block.state.registers
    a, b = get_argument_value(args, 0, regs), get_argument_value(args, 1, regs)
    c = (a * b) % CEILING_256_VALUE
    if is_concrete(c):
        if a != 0 and c // a != b:
            model = {
                'a': a,
                'b': b
            }
            return Vulnerability(INTEGER_OVERFLOW_TYPE, analyzed_block, instruction.offset,
                                 instruction.instruction_offset, model)
    else:
        s = __get_solver(vulnerability_finder.Z3_TIMEOUT * 1000)
        s.add(all_constraints)
        s.add(Not(BVMulNoOverflow(a, b, False)))
        if s.check() == sat:
            return Vulnerability(INTEGER_OVERFLOW_TYPE, analyzed_block, instruction.offset,
                                 instruction.instruction_offset, __extract_values(s.model(), a, b))


def __integer_overflow_analyse(instruction, instruction_name, analyzed_block, all_constraints):
    if instruction_name == ADD:
        return __handle_add_overflow(instruction, analyzed_block, all_constraints)
    elif instruction_name == MUL:
        return __handle_mul_overflow(instruction, analyzed_block, all_constraints)


def __handle_sub_underflow(instruction, analyzed_block, all_constraints):
    args = instruction.arguments
    regs = analyzed_block.state.registers
    a, b = get_argument_value(args, 0, regs), get_argument_value(args, 1, regs)
    if is_all_concrete(a, b):
        if b > a:
            model = {
                'a': a,
                'b': b
            }
            return Vulnerability(INTEGER_UNDERFLOW_TYPE, analyzed_block, instruction.offset,
                                 instruction.instruction_offset, model)
    else:
        s = __get_solver()
        s.add(all_constraints)
        s.add(UGT(b, a))
        if s.check() == sat:
            return Vulnerability(INTEGER_UNDERFLOW_TYPE, analyzed_block, instruction.offset,
                                 instruction.instruction_offset, __extract_values(s.model(), a, b))


def __integer_underflow_analyse(instruction, analyzed_block, all_constraints):
    return __handle_sub_underflow(instruction, analyzed_block, all_constraints)


def arithmetic_analyse(traces: [Trace], find_all):
    all_vulns = set()
    analyzed_blocks = set()
    was_mul_with_256 = False
    was_exp_with_256 = False
    next_trace = False
    for trace in traces:
        if trace.state.reverted:
            continue
        all_constraints = trace.constraints
        for analyzed_block in trace.analyzed_blocks:
            if analyzed_block in analyzed_blocks:
                continue
            for instruction in analyzed_block.block.insns:
                instruction_name = instruction.insn.name
                registers = analyzed_block.state.registers
                args = instruction.arguments
                if instruction_name == ADD or instruction_name == MUL:
                    if instruction_name == MUL:
                        a = get_argument_value(args, 0, registers)
                        if is_concrete(a) and a == 256:
                            was_mul_with_256 = True

                    vuln = __integer_overflow_analyse(instruction, instruction_name, analyzed_block, all_constraints)
                    if vuln:
                        all_vulns.add(vuln)
                        if not find_all:
                            return all_vulns
                elif instruction_name == SUB:
                    if was_mul_with_256 or was_exp_with_256:
                        was_mul_with_256 = False
                        was_exp_with_256 = False
                        b = get_argument_value(args, 1, registers)
                        if is_concrete(b) and b == 1:
                            next_trace = True
                            break

                    vuln = __integer_underflow_analyse(instruction, analyzed_block, all_constraints)
                    if vuln:
                        all_vulns.add(vuln)
                        if not find_all:
                            return all_vulns
                elif instruction_name == EXP:
                    a = get_argument_value(args, 0, registers)
                    if is_concrete(a) and a == 256:
                        was_exp_with_256 = True
            analyzed_blocks.add(analyzed_block)
            if next_trace:
                break
        if next_trace:
            next_trace = False
            continue
    return all_vulns
