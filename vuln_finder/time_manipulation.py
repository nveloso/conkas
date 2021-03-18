# Analyse time manipulation vulnerabilities
from z3.z3util import get_vars

from sym_exec.utils import is_concrete, get_argument_value, is_symbolic
from vuln_finder.vulnerability import Vulnerability

TIME_MANIPULATION_VAR = 'timestamp'
TIME_MANIPULATION_TYPE = 'Time Manipulation'
SHA3 = 'SHA3'
SSTORE = 'SSTORE'


# Return AnalyzedBlock object where the constraint happens
def __get_block_with_constraint(trace, constraint):
    found = False
    for block in reversed(trace.analyzed_blocks):
        if found and hash(constraint) != hash(block.constraints[-1]):
            return block
        if not found and len(block.constraints) > 0 and hash(constraint) == hash(block.constraints[-1]):
            found = True


def __is_based_on_time(data):
    for var in get_vars(data):
        var_name = str(var)
        if var_name == TIME_MANIPULATION_VAR:
            return True
    return False


def __check_if_constraint_is_based_on_time(trace, all_constraints, find_all):
    vulns = set()
    for constraint in all_constraints:
        based_on_time = __is_based_on_time(constraint)
        if not based_on_time:
            continue

        analyzed_block = __get_block_with_constraint(trace, constraint)
        instruction = analyzed_block.block.insns[-1]
        vulns.add(
            Vulnerability(TIME_MANIPULATION_TYPE, analyzed_block, instruction.offset, instruction.instruction_offset))
        if not find_all:
            return vulns
    return vulns


def __check_return_data_is_based_on_time(trace):
    return_data = trace.state.return_data
    if return_data is None or is_concrete(return_data):
        return
    based_on_time = __is_based_on_time(return_data)
    if not based_on_time:
        return
    analyzed_block = trace.analyzed_blocks[-1]
    instruction = analyzed_block.block.insns[-1]
    return Vulnerability(TIME_MANIPULATION_TYPE, analyzed_block, instruction.offset, instruction.instruction_offset)


def __analyse_return_value_and_constraints(trace, find_all):
    all_vulns = set()
    vulns = __check_if_constraint_is_based_on_time(trace, trace.constraints, find_all)
    if vulns:
        all_vulns.update(vulns)
        if not find_all:
            return all_vulns

    vuln = __check_return_data_is_based_on_time(trace)
    if vuln:
        all_vulns.add(vuln)
        if not find_all:
            return all_vulns
    return all_vulns


def analyze_sha3(analyzed_block, instruction):
    args = instruction.arguments
    state = analyzed_block.state
    registers = state.registers
    offset, length = get_argument_value(args, 0, registers), get_argument_value(args, 1, registers)
    if is_symbolic(offset) or is_symbolic(length):
        return
    if length == 0:
        return
    mem = state.memory
    mem.extend(offset, length)
    val = mem.load(offset, length, read_as_bytes=True)
    if not is_symbolic(val):
        return
    based_on_time = __is_based_on_time(val)
    if not based_on_time:
        return
    return Vulnerability(TIME_MANIPULATION_TYPE, analyzed_block, instruction.offset, instruction.instruction_offset)


def analyze_sstore(analyzed_block, instruction):
    value = get_argument_value(instruction.arguments, 1, analyzed_block.state.registers)
    if is_concrete(value):
        return
    based_on_time = __is_based_on_time(value)
    if not based_on_time:
        return
    return Vulnerability(TIME_MANIPULATION_TYPE, analyzed_block, instruction.offset, instruction.instruction_offset)


def time_manipulation_analyse(traces, find_all):
    all_vulns = set()
    analyzed_blocks = set()
    for trace in traces:
        if trace.state.reverted:
            continue
        vulns = __analyse_return_value_and_constraints(trace, find_all)
        if vulns:
            all_vulns.update(vulns)
            if not find_all:
                return all_vulns
        for analyzed_block in trace.analyzed_blocks:
            if analyzed_block in analyzed_blocks:
                continue
            for instruction in analyzed_block.block.insns:
                instruction_name = instruction.insn.name
                vuln = None
                if instruction_name == SHA3:
                    vuln = analyze_sha3(analyzed_block, instruction)
                elif instruction_name == SSTORE:
                    vuln = analyze_sstore(analyzed_block, instruction)
                if vuln:
                    all_vulns.add(vuln)
                    if not find_all:
                        return all_vulns

            analyzed_blocks.add(analyzed_block)

    return all_vulns
