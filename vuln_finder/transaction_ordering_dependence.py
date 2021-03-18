from sym_exec.utils import get_argument_value, is_concrete
from vuln_finder.vulnerability import Vulnerability

CALL_WITH_VALUES = ('CALL', 'CALLCODE')
TRANSACTION_ORDERING_DEPENDENCE_TYPE = 'Transaction Ordering Dependence'


def __get_symbolic_storage_value_of_call(analyzed_block, instruction):
    call_value = get_argument_value(instruction.arguments, 2, analyzed_block.state.registers)
    if is_concrete(call_value):
        return
    bv_name = str(call_value)
    info = bv_name.split(',')
    if not info or 'storage' not in info[0]:
        return
    storage_position = int(info[1])
    return storage_position, call_value


def tod_analyse(traces, find_all):
    all_vulns = set()
    analyzed_blocks = set()
    interesting_values_in_call = []
    interesting_storages = []
    for trace in traces:
        if trace.state.reverted:
            continue
        for analyzed_block in trace.analyzed_blocks:
            if analyzed_block in analyzed_blocks:
                continue
            for instruction in analyzed_block.block.insns:
                instruction_name = instruction.insn.name
                if instruction_name in CALL_WITH_VALUES:
                    storage_value = __get_symbolic_storage_value_of_call(analyzed_block, instruction)
                    if storage_value:
                        interesting_values_in_call.append(dict([(storage_value, (analyzed_block, instruction))]))
            analyzed_blocks.add(analyzed_block)
        interesting_storages.append(trace.state.storage)

    for call in interesting_values_in_call:
        for key, value in call.items():
            for storage in interesting_storages:
                another_value = storage.get(key[0])
                if another_value is not None and hash(another_value) != hash(key[1]):
                    instruction = value[1]
                    all_vulns.add(Vulnerability(TRANSACTION_ORDERING_DEPENDENCE_TYPE, value[0], instruction.offset,
                                                instruction.instruction_offset))
                    if not find_all:
                        return all_vulns
    return all_vulns
