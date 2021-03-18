import unittest

from z3 import BitVec

from rattle import SSABasicBlock, SSAFunction, StackValue, PHIInstruction
from sym_exec.instructions.rattle_instructions import *
from sym_exec.state import State
from sym_exec.utils import WORD_SIZE


class TestRattleInstructions(unittest.TestCase):
    CONDICALL_INST = 'CONDICALL'
    ICALL_INST = 'ICALL'
    PHI_INST = 'PHI'

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

    ################ CONDICALL #####################
    def test_condicall_false_condition(self):
        target = 0xcafe
        condition = 0
        condition_idx = 0
        test_function = SSAFunction(0)
        test_block = SSABasicBlock(0, test_function)
        fallthrough_block = SSABasicBlock(1, test_function)
        test_function.add_block(fallthrough_block)
        test_block.set_fallthrough_target(1)
        target_function = SSAFunction(target)
        target_block = SSABasicBlock(target, target_function)
        target_function.add_block(target_block)
        expected = [(fallthrough_block, None)]

        self.instruction = ConditionalInternalCall(target_function, 1, 0xca, test_block)
        self.state.registers.set(condition_idx, condition)
        self.instruction.append_argument(StackValue(condition_idx))

        actual = inst_condicall(self.instruction, self.state)

        self.assertEqual(expected, actual)

    def test_condicall_true_condition(self):
        target = 0xcafe
        condition = 1
        condition_idx = 0
        test_function = SSAFunction(0)
        test_block = SSABasicBlock(0, test_function)
        fallthrough_block = SSABasicBlock(1, test_function)
        test_function.add_block(fallthrough_block)
        test_block.set_fallthrough_target(1)
        target_function = SSAFunction(target)
        target_block = SSABasicBlock(target, target_function)
        target_function.add_block(target_block)
        expected = [(target_block, None)]

        self.instruction = ConditionalInternalCall(target_function, 1, 0xca, test_block)
        self.state.registers.set(condition_idx, condition)
        self.instruction.append_argument(StackValue(condition_idx))

        actual = inst_condicall(self.instruction, self.state)

        self.assertEqual(expected, actual)

    def test_condicall_symbolic_condition(self):
        target = 0xcafe
        condition = BitVec('x', WORD_SIZE)
        condition_idx = 0
        test_function = SSAFunction(0)
        test_block = SSABasicBlock(0, test_function)
        fallthrough_block = SSABasicBlock(1, test_function)
        test_function.add_block(fallthrough_block)
        test_block.set_fallthrough_target(1)
        target_function = SSAFunction(target)
        target_block = SSABasicBlock(target, target_function)
        target_function.add_block(target_block)
        expected = [(fallthrough_block, condition == 0), (target_block, condition != 0)]

        self.instruction = ConditionalInternalCall(target_function, 1, 0xca, test_block)
        self.state.registers.set(condition_idx, condition)
        self.instruction.append_argument(StackValue(condition_idx))

        actual = inst_condicall(self.instruction, self.state)

        self.assertEqual(expected, actual)

    ################ ICALL #####################
    def test_icall(self):
        target = 0xcafe
        test_function = SSAFunction(0)
        test_block = SSABasicBlock(0, test_function)
        target_function = SSAFunction(target)
        target_block = SSABasicBlock(target, target_function)
        target_function.add_block(target_block)
        expected = [(target_block, None)]

        self.instruction = InternalCall(target_function, 0, 0xca, test_block)
        actual = inst_icall(self.instruction, self.state)

        self.assertEqual(expected, actual)

    ################ PHI #####################
    def test_phi_concrete_value(self):
        phi = PHIInstruction(2, None)
        test_function = SSAFunction(0)
        test_block = SSABasicBlock(0, test_function)
        first_arg_idx = 1
        second_arg = 0xbabe
        second_arg_idx = 2
        return_idx = 0
        expected = 0xbabe

        self.instruction = SSAInstruction(phi, test_block)
        self.instruction.append_argument(StackValue(first_arg_idx))
        self.state.registers.set(second_arg_idx, second_arg)
        self.instruction.append_argument(StackValue(second_arg_idx))
        self.instruction.return_value = StackValue(return_idx)

        inst_phi(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_phi_symbolic_value(self):
        phi = PHIInstruction(3, None)
        test_function = SSAFunction(0)
        test_block = SSABasicBlock(0, test_function)
        first_arg_idx = 1
        second_arg_idx = 2
        third_arg = BitVec('x', WORD_SIZE)
        third_arg_idx = 3
        return_idx = 0
        expected = BitVec('x', WORD_SIZE)

        self.instruction = SSAInstruction(phi, test_block)
        self.instruction.append_argument(StackValue(first_arg_idx))
        self.instruction.append_argument(StackValue(second_arg_idx))
        self.state.registers.set(third_arg_idx, third_arg)
        self.instruction.append_argument(StackValue(third_arg_idx))
        self.instruction.return_value = StackValue(return_idx)

        inst_phi(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)
