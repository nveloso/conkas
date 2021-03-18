# Analyse unchecked low level calls vulnerabilities
import logging

from z3.z3util import get_vars

from sym_exec import symbolic_executor
from sym_exec.trace import Trace
from vuln_finder.vulnerability import Vulnerability

instructions_to_check = ('CALL', 'CALLCODE', 'DELEGATECALL', 'STATICCALL')
logger = logging.getLogger(__name__)
UNCHECKED_LL_CALL_TYPE = 'Unchecked Low Level Call'


def __handle_low_level_call(instruction, remaining_constraints, analyzed_block):
    rv = str(instruction.return_value.value)
    has_return_value_check = False
    for remaining_constraint in remaining_constraints:
        for var in get_vars(remaining_constraint):
            if var.decl().name() == rv:
                has_return_value_check = True

    if not has_return_value_check:
        return Vulnerability(UNCHECKED_LL_CALL_TYPE, analyzed_block, instruction.offset, instruction.instruction_offset)


def unchecked_low_level_calls_analyse(traces: [Trace], find_all):
    all_vulns = set()
    analyzed_blocks = set()
    for trace in traces:
        if trace.state.reverted:
            continue
        if trace.depth >= symbolic_executor.MAX_DEPTH:
            continue
        for analyzed_block in trace.analyzed_blocks:
            if analyzed_block in analyzed_blocks:
                continue
            for instruction in analyzed_block.block.insns:
                instruction_name = instruction.insn.name
                if instruction_name in instructions_to_check:
                    analyzed_constraints = set(analyzed_block.constraints)
                    remaining_constraints = [c for c in trace.constraints if c not in analyzed_constraints]
                    if not remaining_constraints:
                        vuln = Vulnerability(UNCHECKED_LL_CALL_TYPE, analyzed_block, instruction.offset,
                                             instruction.instruction_offset)
                        all_vulns.add(vuln)
                        if not find_all:
                            return all_vulns
                        continue
                    vuln = __handle_low_level_call(instruction, remaining_constraints, analyzed_block)
                    if vuln:
                        all_vulns.add(vuln)
                        if not find_all:
                            return all_vulns
            analyzed_blocks.add(analyzed_block)
    return all_vulns
