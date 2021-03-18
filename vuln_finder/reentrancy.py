# Analyse reentrancy vulnerabilities
from z3 import is_false, is_true, Solver, sat, simplify
from z3.z3util import get_vars

from rattle import SSABasicBlock
from sym_exec.trace import Trace
from sym_exec.utils import get_argument_value, is_symbolic
from vuln_finder import vulnerability_finder
from vuln_finder.vulnerability import Vulnerability

REENTRANCY_TYPE = 'Reentrancy'
CALL_INSTRUCTION = 'CALL'
SSTORE_INSTRUCTION = 'SSTORE'


def __find_instruction(block: SSABasicBlock, instruction_name: str):
    instructions = []
    for instruction in block.insns:
        if instruction.insn.name == instruction_name:
            instructions.append(instruction)
    return instructions


def __get_storage_position(info, state):
    if info and 'storage' not in info[0]:
        return
    storage_position = int(info[1])
    is_storage_position_symbolic = info[2] == 'sym'
    if is_storage_position_symbolic:
        storage_position = state.registers.get(storage_position)
    return storage_position


def __get_storage_var(var_name, state, sstores):
    info = var_name.split(',')
    storage_position = __get_storage_position(info, state)
    if storage_position is None:
        return
    ssa_store_position = -1
    for sstore in sstores:
        idx = get_argument_value(sstore.arguments, 0, state.registers)
        if idx == storage_position:
            ssa_store_position -= 1
    return state.storage.get(storage_position, ssa_store_position)


def __get_solver():
    s = Solver()
    s.set('timeout', vulnerability_finder.Z3_TIMEOUT)
    return s


def __has_vulnerability(constraints):
    s = __get_solver()
    s.add(constraints)
    return s.check() == sat


def __reentrancy_pre_call(analyzed_block, sstores, call_value):
    constraints = []
    # Check if guard is not detected
    for constraint in analyzed_block.constraints:
        constraint = simplify(constraint)
        for var in get_vars(constraint):
            var_name = var.decl().name()
            storage_var = __get_storage_var(var_name, analyzed_block.state, sstores)
            if storage_var is None:
                continue
            constraints.append(constraint)
            constraints.append(var == storage_var)

    # Check if value of storage is different than 0
    if is_symbolic(call_value):
        if call_value.num_args() != 0:
            constraints.append(True)
            return constraints
        bv_name = str(call_value)
        storage_var = __get_storage_var(bv_name, analyzed_block.state, sstores)
        if storage_var is not None:
            constraints.append(storage_var != 0)

    return constraints


# Return AnalyzedBlock object where the constraint happens
def __get_block_with_constraint(constraint, trace):
    found = False
    for block in reversed(trace.analyzed_blocks):
        if found and hash(constraint) != hash(block.constraints[-1]):
            return block
        if not found and len(block.constraints) > 0 and hash(constraint) == hash(block.constraints[-1]):
            found = True


def __reentrancy_pos_call(trace, analyzed_block):
    analyzed_constraints = set(analyzed_block.constraints)
    remaining_constraints = [c for c in trace.constraints if c not in analyzed_constraints]
    for constraint in reversed(remaining_constraints):
        block = __get_block_with_constraint(constraint, trace)
        for var in get_vars(constraint):
            var_name = var.decl().name()
            storage_var = __get_storage_var(var_name, block.state, [])
            if storage_var is None:
                continue

            s = __get_solver()
            s.add(var != storage_var)
            simplified_constraint = simplify(constraint)
            if s.check() != sat:
                if is_false(simplified_constraint):
                    return [False]  # Impossible path
                return []  # No constraints, need to check reentrancy_pre_call
            if is_true(simplified_constraint):
                return [False]  # Protected, no vulnerability
            if is_false(simplified_constraint):
                return [True]  # Non protected, vulnerability
            return [True]  # Could be false positive

    return []


def reentrancy_analyse(traces: [Trace], find_all):
    all_vulns = set()
    analyzed_constraints = False
    exist_constraints = False
    block_analyzed = None
    analyzed_blocks = set()
    offset = None
    instruction_offset = None
    for trace in traces:
        if trace.state.reverted:
            continue
        for analyzed_block in trace.analyzed_blocks:
            if analyzed_block in analyzed_blocks:
                continue
            for instruction in analyzed_block.block.insns:
                instruction_name = instruction.insn.name
                if instruction_name != CALL_INSTRUCTION:
                    continue

                analyzed_constraints = True
                block_analyzed = analyzed_block
                offset = instruction.offset
                instruction_offset = instruction.instruction_offset

                constraints = __reentrancy_pos_call(trace, analyzed_block)
                if constraints:
                    exist_constraints = True
                    if __has_vulnerability(constraints):
                        vuln = Vulnerability(REENTRANCY_TYPE, analyzed_block, offset, instruction_offset)
                        all_vulns.add(vuln)
                        if not find_all:
                            return all_vulns
                    continue

                sstores = list(
                    filter(lambda x: x.offset > instruction.offset,
                           __find_instruction(analyzed_block.block, SSTORE_INSTRUCTION)))
                call_value = get_argument_value(instruction.arguments, 2, analyzed_block.state.registers)
                constraints = __reentrancy_pre_call(analyzed_block, sstores, call_value)
                if constraints:
                    exist_constraints = True
                    if __has_vulnerability(constraints):
                        vuln = Vulnerability(REENTRANCY_TYPE, analyzed_block, offset, instruction_offset)
                        all_vulns.add(vuln)
                        if not find_all:
                            return all_vulns
            analyzed_blocks.add(analyzed_block)

        if analyzed_constraints and not exist_constraints:
            vuln = Vulnerability(REENTRANCY_TYPE, block_analyzed, offset, instruction_offset)
            all_vulns.add(vuln)
            if not find_all:
                return all_vulns
        analyzed_constraints = False
        exist_constraints = False
        block_analyzed = None
    return all_vulns
