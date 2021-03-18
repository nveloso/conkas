import unittest

from z3 import BitVec

from rattle import EVMAsm, SSABasicBlock, SSAFunction, StackValue
from sym_exec.instructions.logging import *
from sym_exec.state import State
from sym_exec.utils import *


class TestLogging(unittest.TestCase):
    LOG0_INST = 'LOG0'
    LOG1_INST = 'LOG1'
    LOG2_INST = 'LOG2'
    LOG3_INST = 'LOG3'
    LOG4_INST = 'LOG4'

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

    ################ LOG0 #####################
    def test_log0_all_concrete_values(self):
        offset = 0
        length = 5
        expected = 32

        self.create_instruction(self.LOG0_INST)
        self.instruction.append_argument(ConcreteStackValue(offset))
        self.instruction.append_argument(ConcreteStackValue(length))

        inst_log0(self.instruction, self.state)

        self.assertEqual(expected, self.state.memory.size)

    def test_log0_symbolic_offset(self):
        offset = BitVec('offset', WORD_SIZE)
        offset_idx = 0
        length = 5
        expected = 0

        self.create_instruction(self.LOG0_INST)
        self.state.registers.set(offset_idx, offset)
        self.instruction.append_argument(StackValue(offset_idx))
        self.instruction.append_argument(ConcreteStackValue(length))

        inst_log0(self.instruction, self.state)

        self.assertEqual(expected, self.state.memory.size)

    def test_log0_symbolic_length(self):
        offset = 0
        length = BitVec('length', WORD_SIZE)
        length_idx = 0
        expected = 0

        self.create_instruction(self.LOG0_INST)
        self.instruction.append_argument(ConcreteStackValue(offset))
        self.state.registers.set(length_idx, length)
        self.instruction.append_argument(StackValue(length_idx))

        inst_log0(self.instruction, self.state)

        self.assertEqual(expected, self.state.memory.size)

    ################ LOG1 #####################
    def test_log1_all_concrete_values(self):
        offset = 0
        length = 5
        topic0 = 123
        expected = 32

        self.create_instruction(self.LOG1_INST)
        self.instruction.append_argument(ConcreteStackValue(offset))
        self.instruction.append_argument(ConcreteStackValue(length))
        self.instruction.append_argument(ConcreteStackValue(topic0))

        inst_log1(self.instruction, self.state)

        self.assertEqual(expected, self.state.memory.size)

    def test_log1_symbolic_offset(self):
        offset = BitVec('offset', WORD_SIZE)
        offset_idx = 0
        length = 5
        topic0 = 123
        expected = 0

        self.create_instruction(self.LOG1_INST)
        self.state.registers.set(offset_idx, offset)
        self.instruction.append_argument(StackValue(offset_idx))
        self.instruction.append_argument(ConcreteStackValue(length))
        self.instruction.append_argument(ConcreteStackValue(topic0))

        inst_log1(self.instruction, self.state)

        self.assertEqual(expected, self.state.memory.size)

    def test_log1_symbolic_length(self):
        offset = 0
        length = BitVec('length', WORD_SIZE)
        length_idx = 0
        topic0 = 123
        expected = 0

        self.create_instruction(self.LOG1_INST)
        self.instruction.append_argument(ConcreteStackValue(offset))
        self.state.registers.set(length_idx, length)
        self.instruction.append_argument(StackValue(length_idx))
        self.instruction.append_argument(ConcreteStackValue(topic0))

        inst_log1(self.instruction, self.state)

        self.assertEqual(expected, self.state.memory.size)

    ################ LOG2 #####################
    def test_log2_all_concrete_values(self):
        offset = 0
        length = 5
        topic0 = 123
        topic1 = 321
        expected = 32

        self.create_instruction(self.LOG2_INST)
        self.instruction.append_argument(ConcreteStackValue(offset))
        self.instruction.append_argument(ConcreteStackValue(length))
        self.instruction.append_argument(ConcreteStackValue(topic0))
        self.instruction.append_argument(ConcreteStackValue(topic1))

        inst_log2(self.instruction, self.state)

        self.assertEqual(expected, self.state.memory.size)

    def test_log2_symbolic_offset(self):
        offset = BitVec('offset', WORD_SIZE)
        offset_idx = 0
        length = 5
        topic0 = 123
        topic1 = 321
        expected = 0

        self.create_instruction(self.LOG2_INST)
        self.state.registers.set(offset_idx, offset)
        self.instruction.append_argument(StackValue(offset_idx))
        self.instruction.append_argument(ConcreteStackValue(length))
        self.instruction.append_argument(ConcreteStackValue(topic0))
        self.instruction.append_argument(ConcreteStackValue(topic1))

        inst_log2(self.instruction, self.state)

        self.assertEqual(expected, self.state.memory.size)

    def test_log2_symbolic_length(self):
        offset = 0
        length = BitVec('length', WORD_SIZE)
        length_idx = 0
        topic0 = 123
        topic1 = 321
        expected = 0

        self.create_instruction(self.LOG2_INST)
        self.instruction.append_argument(ConcreteStackValue(offset))
        self.state.registers.set(length_idx, length)
        self.instruction.append_argument(StackValue(length_idx))
        self.instruction.append_argument(ConcreteStackValue(topic0))
        self.instruction.append_argument(ConcreteStackValue(topic1))

        inst_log2(self.instruction, self.state)

        self.assertEqual(expected, self.state.memory.size)

    ################ LOG3 #####################
    def test_log3_all_concrete_values(self):
        offset = 0
        length = 5
        topic0 = 123
        topic1 = 321
        topic2 = 789
        expected = 32

        self.create_instruction(self.LOG3_INST)
        self.instruction.append_argument(ConcreteStackValue(offset))
        self.instruction.append_argument(ConcreteStackValue(length))
        self.instruction.append_argument(ConcreteStackValue(topic0))
        self.instruction.append_argument(ConcreteStackValue(topic1))
        self.instruction.append_argument(ConcreteStackValue(topic2))

        inst_log3(self.instruction, self.state)

        self.assertEqual(expected, self.state.memory.size)

    def test_log3_symbolic_offset(self):
        offset = BitVec('offset', WORD_SIZE)
        offset_idx = 0
        length = 5
        topic0 = 123
        topic1 = 321
        topic2 = 789
        expected = 0

        self.create_instruction(self.LOG3_INST)
        self.state.registers.set(offset_idx, offset)
        self.instruction.append_argument(StackValue(offset_idx))
        self.instruction.append_argument(ConcreteStackValue(length))
        self.instruction.append_argument(ConcreteStackValue(topic0))
        self.instruction.append_argument(ConcreteStackValue(topic1))
        self.instruction.append_argument(ConcreteStackValue(topic2))

        inst_log3(self.instruction, self.state)

        self.assertEqual(expected, self.state.memory.size)

    def test_log3_symbolic_length(self):
        offset = 0
        length = BitVec('length', WORD_SIZE)
        length_idx = 0
        topic0 = 123
        topic1 = 321
        topic2 = 789
        expected = 0

        self.create_instruction(self.LOG3_INST)
        self.instruction.append_argument(ConcreteStackValue(offset))
        self.state.registers.set(length_idx, length)
        self.instruction.append_argument(StackValue(length_idx))
        self.instruction.append_argument(ConcreteStackValue(topic0))
        self.instruction.append_argument(ConcreteStackValue(topic1))
        self.instruction.append_argument(ConcreteStackValue(topic2))

        inst_log3(self.instruction, self.state)

        self.assertEqual(expected, self.state.memory.size)

    ################ LOG4 #####################
    def test_log4_all_concrete_values(self):
        offset = 0
        length = 5
        topic0 = 123
        topic1 = 321
        topic2 = 789
        topic3 = 987
        expected = 32

        self.create_instruction(self.LOG4_INST)
        self.instruction.append_argument(ConcreteStackValue(offset))
        self.instruction.append_argument(ConcreteStackValue(length))
        self.instruction.append_argument(ConcreteStackValue(topic0))
        self.instruction.append_argument(ConcreteStackValue(topic1))
        self.instruction.append_argument(ConcreteStackValue(topic2))
        self.instruction.append_argument(ConcreteStackValue(topic3))

        inst_log4(self.instruction, self.state)

        self.assertEqual(expected, self.state.memory.size)

    def test_log4_symbolic_offset(self):
        offset = BitVec('offset', WORD_SIZE)
        offset_idx = 0
        length = 5
        topic0 = 123
        topic1 = 321
        topic2 = 789
        topic3 = 987
        expected = 0

        self.create_instruction(self.LOG4_INST)
        self.state.registers.set(offset_idx, offset)
        self.instruction.append_argument(StackValue(offset_idx))
        self.instruction.append_argument(ConcreteStackValue(length))
        self.instruction.append_argument(ConcreteStackValue(topic0))
        self.instruction.append_argument(ConcreteStackValue(topic1))
        self.instruction.append_argument(ConcreteStackValue(topic2))
        self.instruction.append_argument(ConcreteStackValue(topic3))

        inst_log4(self.instruction, self.state)

        self.assertEqual(expected, self.state.memory.size)

    def test_log4_symbolic_length(self):
        offset = 0
        length = BitVec('length', WORD_SIZE)
        length_idx = 0
        topic0 = 123
        topic1 = 321
        topic2 = 789
        topic3 = 987
        expected = 0

        self.create_instruction(self.LOG4_INST)
        self.instruction.append_argument(ConcreteStackValue(offset))
        self.state.registers.set(length_idx, length)
        self.instruction.append_argument(StackValue(length_idx))
        self.instruction.append_argument(ConcreteStackValue(topic0))
        self.instruction.append_argument(ConcreteStackValue(topic1))
        self.instruction.append_argument(ConcreteStackValue(topic2))
        self.instruction.append_argument(ConcreteStackValue(topic3))

        inst_log4(self.instruction, self.state)

        self.assertEqual(expected, self.state.memory.size)
