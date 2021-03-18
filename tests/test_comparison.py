import unittest

from rattle import EVMAsm, SSABasicBlock, SSAFunction, StackValue
from sym_exec.instructions.comparison import *
from sym_exec.state import State
from sym_exec.utils import *


class TestComparison(unittest.TestCase):
    LT_INST = 'LT'
    GT_INST = 'GT'
    SLT_INST = 'SLT'
    SGT_INST = 'SGT'
    EQ_INST = 'EQ'
    ISZERO_INST = 'ISZERO'
    AND_INST = 'AND'
    OR_INST = 'OR'
    XOR_INST = 'XOR'
    NOT_INST = 'NOT'
    BYTE_INST = 'BYTE'

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

    ################ LT #####################
    def test_lt_two_concrete_values(self):
        a = 5
        b = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
        return_idx = 0
        expected = 1
        self.create_instruction(self.LT_INST)

        self.instruction.append_argument(ConcreteStackValue(a))
        self.instruction.append_argument(ConcreteStackValue(b))
        self.instruction.return_value = StackValue(return_idx)

        inst_lt(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_lt_equal_values(self):
        a = 5
        b = 5
        return_idx = 0
        expected = 0

        self.create_instruction(self.LT_INST)
        self.instruction.append_argument(ConcreteStackValue(a))
        self.instruction.append_argument(ConcreteStackValue(b))
        self.instruction.return_value = StackValue(return_idx)

        inst_lt(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_lt_symbolic(self):
        sym_a = BitVec('%2', WORD_SIZE)
        b = 4
        sym_a_idx = 1
        return_idx = 0
        expected = If(ULT(sym_a, b), BitVecVal(1, WORD_SIZE), BitVecVal(0, WORD_SIZE))

        self.create_instruction(self.LT_INST)

        self.state.registers.set(sym_a_idx, sym_a)
        self.instruction.append_argument(StackValue(sym_a_idx))
        self.instruction.append_argument(ConcreteStackValue(b))
        self.instruction.return_value = StackValue(return_idx)

        inst_lt(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ GT #####################
    def test_gt_two_concrete_values(self):
        a = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
        b = 5
        return_idx = 0
        expected = 1
        self.create_instruction(self.GT_INST)

        self.instruction.append_argument(ConcreteStackValue(a))
        self.instruction.append_argument(ConcreteStackValue(b))
        self.instruction.return_value = StackValue(return_idx)

        inst_gt(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_gt_equal_values(self):
        a = 5
        b = 5
        return_idx = 0
        expected = 0

        self.create_instruction(self.GT_INST)
        self.instruction.append_argument(ConcreteStackValue(a))
        self.instruction.append_argument(ConcreteStackValue(b))
        self.instruction.return_value = StackValue(return_idx)

        inst_gt(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_gt_symbolic(self):
        sym_a = BitVec('%2', WORD_SIZE)
        b = 4
        sym_a_idx = 1
        return_idx = 0
        expected = If(UGT(sym_a, b), BitVecVal(1, WORD_SIZE), BitVecVal(0, WORD_SIZE))

        self.create_instruction(self.GT_INST)

        self.state.registers.set(sym_a_idx, sym_a)
        self.instruction.append_argument(StackValue(sym_a_idx))
        self.instruction.append_argument(ConcreteStackValue(b))
        self.instruction.return_value = StackValue(return_idx)

        inst_gt(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ SLT #####################
    def test_slt_two_concrete_values(self):
        a = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffe
        b = 5
        return_idx = 0
        expected = 1
        self.create_instruction(self.SLT_INST)

        self.instruction.append_argument(ConcreteStackValue(a))
        self.instruction.append_argument(ConcreteStackValue(b))
        self.instruction.return_value = StackValue(return_idx)

        inst_slt(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_slt_equal_values(self):
        a = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
        b = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
        return_idx = 0
        expected = 0

        self.create_instruction(self.SLT_INST)
        self.instruction.append_argument(ConcreteStackValue(a))
        self.instruction.append_argument(ConcreteStackValue(b))
        self.instruction.return_value = StackValue(return_idx)

        inst_slt(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_slt_symbolic(self):
        sym_a = BitVec('%2', WORD_SIZE)
        b = 4
        sym_a_idx = 1
        return_idx = 0
        expected = If(sym_a < b, BitVecVal(1, WORD_SIZE), BitVecVal(0, WORD_SIZE))

        self.create_instruction(self.SLT_INST)

        self.state.registers.set(sym_a_idx, sym_a)
        self.instruction.append_argument(StackValue(sym_a_idx))
        self.instruction.append_argument(ConcreteStackValue(b))
        self.instruction.return_value = StackValue(return_idx)

        inst_slt(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ SGT #####################
    def test_sgt_two_concrete_values(self):
        a = 5
        b = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
        return_idx = 0
        expected = 1
        self.create_instruction(self.SGT_INST)

        self.instruction.append_argument(ConcreteStackValue(a))
        self.instruction.append_argument(ConcreteStackValue(b))
        self.instruction.return_value = StackValue(return_idx)

        inst_sgt(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_sgt_equal_values(self):
        a = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
        b = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
        return_idx = 0
        expected = 0

        self.create_instruction(self.SGT_INST)
        self.instruction.append_argument(ConcreteStackValue(a))
        self.instruction.append_argument(ConcreteStackValue(b))
        self.instruction.return_value = StackValue(return_idx)

        inst_sgt(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_sgt_symbolic(self):
        sym_a = BitVec('%2', WORD_SIZE)
        b = 4
        sym_a_idx = 1
        return_idx = 0
        expected = If(sym_a > b, BitVecVal(1, WORD_SIZE), BitVecVal(0, WORD_SIZE))

        self.create_instruction(self.SGT_INST)

        self.state.registers.set(sym_a_idx, sym_a)
        self.instruction.append_argument(StackValue(sym_a_idx))
        self.instruction.append_argument(ConcreteStackValue(b))
        self.instruction.return_value = StackValue(return_idx)

        inst_sgt(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ EQ #####################
    def test_eq_two_equal_concrete_values(self):
        a = 5
        b = 5
        return_idx = 0
        expected = 1
        self.create_instruction(self.EQ_INST)

        self.instruction.append_argument(ConcreteStackValue(a))
        self.instruction.append_argument(ConcreteStackValue(b))
        self.instruction.return_value = StackValue(return_idx)

        inst_eq(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_eq_different_values(self):
        a = 0
        b = 1
        return_idx = 0
        expected = 0

        self.create_instruction(self.EQ_INST)
        self.instruction.append_argument(ConcreteStackValue(a))
        self.instruction.append_argument(ConcreteStackValue(b))
        self.instruction.return_value = StackValue(return_idx)

        inst_eq(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_eq_symbolic(self):
        sym_a = BitVec('%2', WORD_SIZE)
        b = 4
        sym_a_idx = 1
        return_idx = 0
        expected = If(sym_a == b, BitVecVal(1, WORD_SIZE), BitVecVal(0, WORD_SIZE))

        self.create_instruction(self.EQ_INST)

        self.state.registers.set(sym_a_idx, sym_a)
        self.instruction.append_argument(StackValue(sym_a_idx))
        self.instruction.append_argument(ConcreteStackValue(b))
        self.instruction.return_value = StackValue(return_idx)

        inst_eq(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ ISZERO #####################
    def test_iszero_zero_value(self):
        a = 0
        return_idx = 0
        expected = 1
        self.create_instruction(self.ISZERO_INST)

        self.instruction.append_argument(ConcreteStackValue(a))
        self.instruction.return_value = StackValue(return_idx)

        inst_iszero(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_iszero_non_zero_value(self):
        a = 52315132
        return_idx = 0
        expected = 0

        self.create_instruction(self.ISZERO_INST)
        self.instruction.append_argument(ConcreteStackValue(a))
        self.instruction.return_value = StackValue(return_idx)

        inst_iszero(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_iszero_symbolic(self):
        sym_a = BitVec('%2', WORD_SIZE)
        sym_a_idx = 1
        return_idx = 0
        expected = If(sym_a == 0, BitVecVal(1, WORD_SIZE), BitVecVal(0, WORD_SIZE))

        self.create_instruction(self.ISZERO_INST)

        self.state.registers.set(sym_a_idx, sym_a)
        self.instruction.append_argument(StackValue(sym_a_idx))
        self.instruction.return_value = StackValue(return_idx)

        inst_iszero(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ AND #####################
    def test_and_concrete_values(self):
        a = 0xcafebabe
        b = 0xdeadbeef
        return_idx = 0
        expected = 0xcaacbaae
        self.create_instruction(self.AND_INST)

        self.instruction.append_argument(ConcreteStackValue(a))
        self.instruction.append_argument(ConcreteStackValue(b))
        self.instruction.return_value = StackValue(return_idx)

        inst_and(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_and_symbolic(self):
        sym_a = BitVec('%2', WORD_SIZE)
        sym_a_idx = 1
        b = 0xdeadbeef
        return_idx = 0
        expected = sym_a & b

        self.create_instruction(self.AND_INST)

        self.state.registers.set(sym_a_idx, sym_a)
        self.instruction.append_argument(StackValue(sym_a_idx))
        self.instruction.append_argument(ConcreteStackValue(b))
        self.instruction.return_value = StackValue(return_idx)

        inst_and(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ OR #####################
    def test_or_concrete_values(self):
        a = 0xcafebabe
        b = 0xdeadbeef
        return_idx = 0
        expected = 0xdeffbeff
        self.create_instruction(self.OR_INST)

        self.instruction.append_argument(ConcreteStackValue(a))
        self.instruction.append_argument(ConcreteStackValue(b))
        self.instruction.return_value = StackValue(return_idx)

        inst_or(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_or_symbolic(self):
        sym_a = BitVec('%2', WORD_SIZE)
        sym_a_idx = 1
        b = 0xdeadbeef
        return_idx = 0
        expected = sym_a | b

        self.create_instruction(self.OR_INST)

        self.state.registers.set(sym_a_idx, sym_a)
        self.instruction.append_argument(StackValue(sym_a_idx))
        self.instruction.append_argument(ConcreteStackValue(b))
        self.instruction.return_value = StackValue(return_idx)

        inst_or(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ XOR #####################
    def test_xor_concrete_values(self):
        a = 0xcafebabe
        b = 0xdeadbeef
        return_idx = 0
        expected = 0x14530451
        self.create_instruction(self.XOR_INST)

        self.instruction.append_argument(ConcreteStackValue(a))
        self.instruction.append_argument(ConcreteStackValue(b))
        self.instruction.return_value = StackValue(return_idx)

        inst_xor(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_xor_symbolic(self):
        sym_a = BitVec('%2', WORD_SIZE)
        sym_a_idx = 1
        b = 0xdeadbeef
        return_idx = 0
        expected = sym_a ^ b

        self.create_instruction(self.XOR_INST)

        self.state.registers.set(sym_a_idx, sym_a)
        self.instruction.append_argument(StackValue(sym_a_idx))
        self.instruction.append_argument(ConcreteStackValue(b))
        self.instruction.return_value = StackValue(return_idx)

        inst_xor(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ NOT #####################
    def test_not_concrete_values(self):
        a = 0xdeadbeef
        return_idx = 0
        expected = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffff21524110
        self.create_instruction(self.NOT_INST)

        self.instruction.append_argument(ConcreteStackValue(a))
        self.instruction.return_value = StackValue(return_idx)

        inst_not(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_not_symbolic(self):
        sym_a = BitVec('%2', WORD_SIZE)
        sym_a_idx = 1
        return_idx = 0
        expected = MAX_UVALUE - sym_a

        self.create_instruction(self.NOT_INST)

        self.state.registers.set(sym_a_idx, sym_a)
        self.instruction.append_argument(StackValue(sym_a_idx))
        self.instruction.return_value = StackValue(return_idx)

        inst_not(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ BYTE #####################
    def test_byte_concrete_values(self):
        i = 30
        x = 0xdeadbeef
        return_idx = 0
        expected = 0xbe
        self.create_instruction(self.BYTE_INST)

        self.instruction.append_argument(ConcreteStackValue(i))
        self.instruction.append_argument(ConcreteStackValue(x))
        self.instruction.return_value = StackValue(return_idx)

        inst_byte(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_byte_i_greater_than_31_concrete_values(self):
        i = 32
        x = 0xdeadbeef
        return_idx = 0
        expected = 0
        self.create_instruction(self.BYTE_INST)

        self.instruction.append_argument(ConcreteStackValue(i))
        self.instruction.append_argument(ConcreteStackValue(x))
        self.instruction.return_value = StackValue(return_idx)

        inst_byte(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_byte_i_symbolic(self):
        sym_i = BitVec('%2', WORD_SIZE)
        sym_i_idx = 1
        x = 0xdeadbeef
        return_idx = 0
        expected = BitVec(str(return_idx), WORD_SIZE)

        self.create_instruction(self.BYTE_INST)

        self.state.registers.set(sym_i_idx, sym_i)
        self.instruction.append_argument(StackValue(sym_i_idx))
        self.instruction.append_argument(ConcreteStackValue(x))
        self.instruction.return_value = StackValue(return_idx)

        inst_byte(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_byte_x_symbolic(self):
        i = 30
        sym_x = BitVec('%2', WORD_SIZE)
        sym_x_idx = 1
        return_idx = 0
        idx = 248 - (i * 8)
        expected = Concat(BitVecVal(0, WORD_SIZE - 8), Extract(idx + 7, idx, sym_x))

        self.create_instruction(self.BYTE_INST)
        self.instruction.append_argument(ConcreteStackValue(i))
        self.state.registers.set(sym_x_idx, sym_x)
        self.instruction.append_argument(StackValue(sym_x_idx))
        self.instruction.return_value = StackValue(return_idx)

        inst_byte(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
