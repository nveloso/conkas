import unittest

from rattle import EVMAsm, SSABasicBlock, SSAFunction, StackValue
from sym_exec.environment import Environment
from sym_exec.instructions.contract_context import *
from sym_exec.state import State
from sym_exec.utils import *


class TestContractContext(unittest.TestCase):
    ADDRESS_INST = 'ADDRESS'
    BALANCE_INST = 'BALANCE'
    ORIGIN_INST = 'ORIGIN'
    CALLER_INST = 'CALLER'
    CALLVALUE_INST = 'CALLVALUE'
    CALLDATALOAD_INST = 'CALLDATALOAD'
    CALLDATASIZE_INST = 'CALLDATASIZE'
    CALLDATACOPY_INST = 'CALLDATACOPY'
    CODESIZE_INST = 'CODESIZE'
    CODECOPY_INST = 'CODECOPY'
    GASPRICE_INST = 'GASPRICE'
    EXTCODESIZE_INST = 'EXTCODESIZE'
    EXTCODECOPY_INST = 'EXTCODECOPY'
    RETURNDATASIZE_INST = 'RETURNDATASIZE'
    RETURNDATACOPY_INST = 'RETURNDATACOPY'
    EXTCODEHASH_INST = 'EXTCODEHASH'

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.state = State()

    def tearDown(self):
        pass

    def create_instruction(self, name, rv=None, concrete_args=None, symbolic_args=None):
        self.instruction = SSAInstruction(EVMAsm.assemble_one(name), SSABasicBlock(0, SSAFunction(0)))
        if rv is not None:
            self.instruction.return_value = StackValue(rv)

        if concrete_args is not None:
            for c_arg in concrete_args:
                self.instruction.append_argument(ConcreteStackValue(c_arg))

        if symbolic_args is not None:
            for s_arg in symbolic_args:
                self.state.registers.set(s_arg, BitVec(str(rv), WORD_SIZE))
                self.instruction.append_argument(StackValue(s_arg))

    ################ ADDRESS #####################
    def test_address_unknown(self):
        return_idx = 0
        expected = BitVec('address', WORD_SIZE)
        self.create_instruction(self.ADDRESS_INST)

        self.instruction.return_value = StackValue(return_idx)

        inst_address(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ BALANCE #####################
    def test_balance_unknown_address(self):
        addr = BitVec('2', WORD_SIZE)
        addr_idx = 1
        return_idx = 0
        expected = BitVec('0', WORD_SIZE)
        self.create_instruction(self.BALANCE_INST)

        self.state.registers.set(addr_idx, addr)
        self.instruction.append_argument(StackValue(addr_idx))
        self.instruction.return_value = StackValue(return_idx)

        inst_balance(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ ORIGIN #####################
    def test_origin_unknown(self):
        return_idx = 0
        expected = BitVec('origin', WORD_SIZE)
        self.create_instruction(self.ORIGIN_INST)

        self.instruction.return_value = StackValue(return_idx)

        inst_origin(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ CALLER #####################
    def test_caller_unknown(self):
        return_idx = 0
        expected = BitVec('caller', WORD_SIZE)
        self.create_instruction(self.CALLER_INST)

        self.instruction.return_value = StackValue(return_idx)

        inst_caller(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ CALLVALUE #####################
    def test_callvalue_unknown(self):
        return_idx = 0
        expected = BitVec('callvalue', WORD_SIZE)
        self.create_instruction(self.CALLVALUE_INST)

        self.instruction.return_value = StackValue(return_idx)

        inst_callvalue(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ CALLDATALOAD #####################
    def test_calldataload_unknown(self):
        i = BitVec('2', WORD_SIZE)
        i_idx = 1
        return_idx = 0
        expected = BitVec(f'calldataload_sym_{i}', WORD_SIZE)
        self.create_instruction(self.CALLDATALOAD_INST)

        self.state.registers.set(i_idx, i)
        self.instruction.append_argument(StackValue(i_idx))
        self.instruction.return_value = StackValue(return_idx)

        inst_calldataload(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ CALLDATASIZE #####################
    def test_calldatasize_unknown(self):
        return_idx = 0
        expected = BitVec('calldatasize', WORD_SIZE)
        self.create_instruction(self.CALLDATASIZE_INST)

        self.instruction.return_value = StackValue(return_idx)

        inst_calldatasize(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ CALLDATACOPY #####################
    def test_calldatacopy_unknown(self):
        destOffset = 16
        offset = 0
        length = 18

        self.create_instruction(self.CALLDATACOPY_INST)
        self.instruction.append_argument(ConcreteStackValue(destOffset))
        self.instruction.append_argument(ConcreteStackValue(offset))
        self.instruction.append_argument(ConcreteStackValue(length))

        expected = BitVec(str(hash(self.instruction)), length * 8)
        inst_calldatacopy(self.instruction, self.state)
        actual = self.state.memory.load(destOffset, length)

        self.assertEqual(expected, actual)

    ################ CODESIZE #####################
    def test_codesize(self):
        self.state = State(environment=Environment(b'60056005023800'))
        return_idx = 0
        self.create_instruction(self.CODESIZE_INST)
        self.instruction.return_value = StackValue(return_idx)
        expected = 7

        inst_codesize(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ CODECOPY #####################
    def test_codecopy_all_concrete(self):
        self.state = State(environment=Environment(b'60056005023800'))
        destOffset = 4
        offset = 1
        length = 3
        expected = 0x056005

        self.create_instruction(self.CODECOPY_INST)
        self.instruction.append_argument(ConcreteStackValue(destOffset))
        self.instruction.append_argument(ConcreteStackValue(offset))
        self.instruction.append_argument(ConcreteStackValue(length))

        inst_codecopy(self.instruction, self.state)
        actual = self.state.memory.load(destOffset, length)

        self.assertEqual(expected, actual)

    def test_codecopy_dest_offset_symbolic(self):
        self.state = State(environment=Environment(b'60056005023800'))
        destOffset = BitVec('x', WORD_SIZE)
        destOffset_idx = 1
        offset = 1
        length = 3
        expected = self.state.memory

        self.create_instruction(self.CODECOPY_INST)
        self.state.registers.set(destOffset_idx, destOffset)
        self.instruction.append_argument(StackValue(destOffset_idx))
        self.instruction.append_argument(ConcreteStackValue(offset))
        self.instruction.append_argument(ConcreteStackValue(length))

        inst_codecopy(self.instruction, self.state)
        actual = self.state.memory

        self.assertEqual(expected, actual)

    def test_codecopy_offset_symbolic(self):
        self.state = State(environment=Environment(b'60056005023800'))
        destOffset = 4
        offset = BitVec('x', WORD_SIZE)
        offset_idx = 1
        length = 3

        self.create_instruction(self.CODECOPY_INST)
        self.instruction.append_argument(ConcreteStackValue(destOffset))
        self.state.registers.set(offset_idx, offset)
        self.instruction.append_argument(StackValue(offset_idx))
        self.instruction.append_argument(ConcreteStackValue(length))

        expected = BitVec(str(hash(self.instruction)), length * 8)
        inst_codecopy(self.instruction, self.state)
        actual = self.state.memory.load(destOffset, length)

        self.assertEqual(expected, actual)

    def test_codecopy_length_symbolic(self):
        self.state = State(environment=Environment(b'60056005023800'))
        destOffset = 4
        offset = 1
        length = BitVec('x', WORD_SIZE)
        length_idx = 1

        self.create_instruction(self.CODECOPY_INST)
        self.instruction.append_argument(ConcreteStackValue(destOffset))
        self.instruction.append_argument(ConcreteStackValue(offset))
        self.state.registers.set(length_idx, length)
        self.instruction.append_argument(StackValue(length_idx))

        expected = BitVec(str(hash(self.instruction)), 8)
        inst_codecopy(self.instruction, self.state)
        actual = self.state.memory.load(destOffset, 1)

        self.assertEqual(expected, actual)

    ################ GASPRICE #####################
    def test_gasprice(self):
        return_idx = 0
        expected = BitVec('gasprice', WORD_SIZE)

        self.create_instruction(self.GASPRICE_INST)
        self.instruction.return_value = StackValue(return_idx)

        inst_gasprice(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ EXTCODESIZE #####################
    def test_extcodesize(self):
        some_address = 0
        return_idx = 0
        expected = BitVec('0', WORD_SIZE)

        self.create_instruction(self.EXTCODESIZE_INST)
        self.instruction.append_argument(ConcreteStackValue(some_address))
        self.instruction.return_value = StackValue(return_idx)

        inst_extcodesize(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ EXTCODECOPY #####################
    def test_extcodecopy_all_concrete(self):
        some_address = 0
        destOffset = 3
        offset = 2
        length = 4

        self.create_instruction(self.EXTCODECOPY_INST)
        self.instruction.append_argument(ConcreteStackValue(some_address))
        self.instruction.append_argument(ConcreteStackValue(destOffset))
        self.instruction.append_argument(ConcreteStackValue(offset))
        self.instruction.append_argument(ConcreteStackValue(length))

        expected = BitVec(str(hash(self.instruction)), length * 8)
        inst_extcodecopy(self.instruction, self.state)
        actual = self.state.memory.load(destOffset, length)

        self.assertEqual(expected, actual)

    def test_extcodecopy_dest_offset_symbolic(self):
        some_address = 0
        destOffset = BitVec('x', WORD_SIZE)
        destOffset_idx = 1
        offset = 2
        length = 4
        expected = self.state.memory

        self.create_instruction(self.EXTCODECOPY_INST)
        self.instruction.append_argument(ConcreteStackValue(some_address))
        self.state.registers.set(destOffset_idx, destOffset)
        self.instruction.append_argument(StackValue(destOffset_idx))
        self.instruction.append_argument(ConcreteStackValue(offset))
        self.instruction.append_argument(ConcreteStackValue(length))

        inst_extcodecopy(self.instruction, self.state)
        actual = self.state.memory

        self.assertEqual(expected, actual)

    def test_extcodecopy_length_symbolic(self):
        some_address = 0
        destOffset = 3
        offset = 2
        length = BitVec('x', WORD_SIZE)
        length_idx = 1

        self.create_instruction(self.EXTCODECOPY_INST)
        self.instruction.append_argument(ConcreteStackValue(some_address))
        self.instruction.append_argument(ConcreteStackValue(destOffset))
        self.instruction.append_argument(ConcreteStackValue(offset))
        self.state.registers.set(length_idx, length)
        self.instruction.append_argument(StackValue(length_idx))

        expected = BitVec(str(hash(self.instruction)), 8)
        inst_extcodecopy(self.instruction, self.state)
        actual = self.state.memory.load(destOffset, 1)

        self.assertEqual(expected, actual)

    ################ RETURNDATASIZE #####################
    def test_returndatasize(self):
        return_idx = 0
        expected = BitVec('0', WORD_SIZE)

        self.create_instruction(self.RETURNDATASIZE_INST)
        self.instruction.return_value = StackValue(return_idx)

        inst_returndatasize(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ RETURNDATACOPY #####################
    def test_returndatacopy_all_concrete(self):
        destOffset = 3
        offset = 2
        length = 4

        self.create_instruction(self.RETURNDATACOPY_INST)
        self.instruction.append_argument(ConcreteStackValue(destOffset))
        self.instruction.append_argument(ConcreteStackValue(offset))
        self.instruction.append_argument(ConcreteStackValue(length))

        expected = BitVec(str(hash(self.instruction)), length * 8)
        inst_returndatacopy(self.instruction, self.state)
        actual = self.state.memory.load(destOffset, length)

        self.assertEqual(expected, actual)

    def test_returndatacopy_dest_offset_symbolic(self):
        destOffset = BitVec('x', WORD_SIZE)
        destOffset_idx = 1
        offset = 2
        length = 4
        expected = self.state.memory

        self.create_instruction(self.RETURNDATACOPY_INST)
        self.state.registers.set(destOffset_idx, destOffset)
        self.instruction.append_argument(StackValue(destOffset_idx))
        self.instruction.append_argument(ConcreteStackValue(offset))
        self.instruction.append_argument(ConcreteStackValue(length))

        inst_returndatacopy(self.instruction, self.state)
        actual = self.state.memory

        self.assertEqual(expected, actual)

    def test_returndatacopy_length_symbolic(self):
        destOffset = 3
        offset = 2
        length = BitVec('x', WORD_SIZE)
        length_idx = 1

        self.create_instruction(self.RETURNDATACOPY_INST)
        self.instruction.append_argument(ConcreteStackValue(destOffset))
        self.instruction.append_argument(ConcreteStackValue(offset))
        self.state.registers.set(length_idx, length)
        self.instruction.append_argument(StackValue(length_idx))

        expected = BitVec(str(hash(self.instruction)), 8)
        inst_returndatacopy(self.instruction, self.state)
        actual = self.state.memory.load(destOffset, 1)

        self.assertEqual(expected, actual)

    ################ EXTCODEHASH #####################
    def test_extcodehash(self):
        some_address = 0
        return_idx = 0
        expected = BitVec('0', WORD_SIZE)

        self.create_instruction(self.EXTCODEHASH_INST)
        self.instruction.append_argument(ConcreteStackValue(some_address))
        self.instruction.return_value = StackValue(return_idx)

        inst_extcodehash(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)
