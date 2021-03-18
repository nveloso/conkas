import logging
from copy import copy
from itertools import chain

from rattle import Recover, SSABasicBlock
from sym_exec.analyzed_block import AnalyzedBlock
from sym_exec.environment import Environment
from sym_exec.instructions import instructions_functions
from sym_exec.state import State
from sym_exec.trace import Trace

logger = logging.getLogger(__name__)
MAX_DEPTH = 25


class SymExec(object):
    def __init__(self, ssa: Recover = None):
        if ssa is None:
            logger.warning("SymExec received nothing to execute")
            return

        if len(ssa.functions) == 0:
            logger.warning("No functions to analyse")
            return

        if len(ssa.functions[0].blocks) == 0:
            logger.warning("No blocks to analyse")
            return

        self._ssa = ssa
        environment = self.__get_environment()

        self._dispatch_trace = Trace(environment=environment)
        dispatch_block = ssa.functions[0].blocks[0]
        self._dispatch_trace.block_to_analyse = dispatch_block
        self._traces = []
        global MAX_DEPTH
        self._max_depth = MAX_DEPTH

    @property
    def traces(self):
        return self._traces

    def __get_environment(self):
        contract_code = self._ssa.internal.filedata
        return Environment(contract_code)

    def execute(self):
        traces_to_execute = [self._dispatch_trace]
        while True:
            new_traces = self.__sym_exec_traces(traces_to_execute)
            self._traces.extend(traces_to_execute)
            if not new_traces:
                break
            traces_to_execute = new_traces

        return self._traces

    def __sym_exec_traces(self, traces):
        new_traces = []
        for trace in traces:
            while trace.block_to_analyse is not None:
                block_to_analyse = trace.block_to_analyse
                new_blocks = self.__sym_exec_block(block_to_analyse, trace.state)
                trace.add_analysed_block(AnalyzedBlock(block_to_analyse, copy(trace.state), trace.constraints.copy()))

                trace.depth += 1
                if trace.depth >= self._max_depth:
                    break

                if not new_blocks:
                    break

                for new_block in new_blocks[1:]:
                    new_trace = copy(trace)
                    new_trace.block_to_analyse = new_block[0]
                    new_trace.current_constraint = new_block[1]
                    new_traces.append(new_trace)

                block_and_constraint = new_blocks[0]
                trace.block_to_analyse = block_and_constraint[0]
                trace.current_constraint = block_and_constraint[1]

            del trace.block_to_analyse
            del trace.current_constraint

        return new_traces

    def __sym_exec_block(self, block: SSABasicBlock, state: State) -> []:
        to_analyse = []

        for instruction in block.insns:
            new_blocks = self.__sym_exec_instruction(instruction, state)
            if not new_blocks:
                if instruction != block.insns[-1]:
                    continue
                fallthrough_block = block.fallthrough_edge
                if fallthrough_block is None:
                    continue
                new_blocks = [(block.fallthrough_edge, None)]

            to_analyse.append(new_blocks)

        return list(chain.from_iterable(to_analyse))

    def __sym_exec_instruction(self, instruction, state):
        if instruction.insn.is_push:
            mnemonic = 'PUSH'
        else:
            mnemonic = instruction.insn.mnemonic

        func = instructions_functions.get(mnemonic, None)
        if func is None:
            logger.error(f"Instruction {mnemonic} is not implemented.")
            raise NotImplementedError
        return func(instruction, state)
