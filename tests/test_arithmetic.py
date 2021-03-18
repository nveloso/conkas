import unittest

from rattle import EVMAsm, SSABasicBlock, SSAFunction, StackValue
from sym_exec.instructions.arithmetic import *
from sym_exec.state import State
from sym_exec.utils import *


class TestArithmetic(unittest.TestCase):
    STOP_INST = 'STOP'
    ADD_INST = 'ADD'
    MUL_INST = 'MUL'
    SUB_INST = 'SUB'
    DIV_INST = 'DIV'
    SDIV_INST = 'SDIV'
    MOD_INST = 'MOD'
    SMOD_INST = 'SMOD'
    ADDMOD_INST = 'ADDMOD'
    MULMOD_INST = 'MULMOD'
    EXP_INST = 'EXP'
    SIGNEXTEND_INST = 'SIGNEXTEND'
    SHL_INST = 'SHL'
    SHR_INST = 'SHR'
    SAR_INST = 'SAR'

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

    ################ STOP #####################
    def test_stop(self):
        self.create_instruction(self.STOP_INST)
        inst_stop(self.instruction, self.state)

        self.assertTrue(self.state.stopped)

    ################ ADD #####################
    def test_add_two_concrete_values(self):
        concrete_arg0 = 4
        concrete_arg1 = 5
        return_idx = 0
        expected = 9
        self.create_instruction(self.ADD_INST)

        self.instruction.append_argument(ConcreteStackValue(concrete_arg0))
        self.instruction.append_argument(ConcreteStackValue(concrete_arg1))
        self.instruction.return_value = StackValue(return_idx)

        inst_add(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_add_concrete_overflow(self):
        concrete_arg0 = MAX_UVALUE
        concrete_arg1 = 255
        return_idx = 0
        expected = 254

        self.create_instruction(self.ADD_INST)
        self.instruction.append_argument(ConcreteStackValue(concrete_arg0))
        self.instruction.append_argument(ConcreteStackValue(concrete_arg1))
        self.instruction.return_value = StackValue(return_idx)

        inst_add(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_add_one_symbolic(self):
        sym_arg = BitVec('%2', WORD_SIZE)
        concrete_arg = 4
        sym_arg_idx = 1
        return_idx = 0
        expected = simplify(concrete_arg + sym_arg)

        self.create_instruction(self.ADD_INST)

        self.instruction.append_argument(ConcreteStackValue(concrete_arg))
        self.state.registers.set(sym_arg_idx, sym_arg)
        self.instruction.append_argument(StackValue(sym_arg_idx))
        self.instruction.return_value = StackValue(return_idx)

        inst_add(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ MUL #####################
    def test_mul_two_concrete_values(self):
        concrete_arg0 = 4
        concrete_arg1 = 5
        return_idx = 0
        expected = 20
        self.create_instruction(self.MUL_INST)

        self.instruction.append_argument(ConcreteStackValue(concrete_arg0))
        self.instruction.append_argument(ConcreteStackValue(concrete_arg1))
        self.instruction.return_value = StackValue(return_idx)

        inst_mul(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_mul_concrete_overflow(self):
        concrete_arg0 = MAX_UVALUE
        concrete_arg1 = 2
        return_idx = 0
        expected = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffe

        self.create_instruction(self.MUL_INST)
        self.instruction.append_argument(ConcreteStackValue(concrete_arg0))
        self.instruction.append_argument(ConcreteStackValue(concrete_arg1))
        self.instruction.return_value = StackValue(return_idx)

        inst_mul(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_mul_one_symbolic(self):
        sym_arg = BitVec('%2', WORD_SIZE)
        concrete_arg = 4
        sym_arg_idx = 1
        return_idx = 0
        expected = simplify(concrete_arg * sym_arg)

        self.create_instruction(self.MUL_INST)

        self.instruction.append_argument(ConcreteStackValue(concrete_arg))
        self.state.registers.set(sym_arg_idx, sym_arg)
        self.instruction.append_argument(StackValue(sym_arg_idx))
        self.instruction.return_value = StackValue(return_idx)

        inst_mul(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ SUB #####################
    def test_sub_two_concrete_values(self):
        concrete_arg0 = 5
        concrete_arg1 = 4
        return_idx = 0
        expected = 1
        self.create_instruction(self.SUB_INST)

        self.instruction.append_argument(ConcreteStackValue(concrete_arg0))
        self.instruction.append_argument(ConcreteStackValue(concrete_arg1))
        self.instruction.return_value = StackValue(return_idx)

        inst_sub(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_sub_concrete_underflow(self):
        concrete_arg0 = 1
        concrete_arg1 = 2
        return_idx = 0
        expected = MAX_UVALUE

        self.create_instruction(self.SUB_INST)
        self.instruction.append_argument(ConcreteStackValue(concrete_arg0))
        self.instruction.append_argument(ConcreteStackValue(concrete_arg1))
        self.instruction.return_value = StackValue(return_idx)

        inst_sub(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_sub_one_symbolic(self):
        concrete_arg = 4
        sym_arg = BitVec('%2', WORD_SIZE)
        sym_arg_idx = 1
        return_idx = 0
        expected = simplify(concrete_arg - sym_arg)

        self.create_instruction(self.SUB_INST)

        self.instruction.append_argument(ConcreteStackValue(concrete_arg))
        self.state.registers.set(sym_arg_idx, sym_arg)
        self.instruction.append_argument(StackValue(sym_arg_idx))
        self.instruction.return_value = StackValue(return_idx)

        inst_sub(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ DIV #####################
    def test_div_two_concrete_values(self):
        concrete_arg0 = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffe
        concrete_arg1 = 2
        return_idx = 0
        expected = 0x7fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
        self.create_instruction(self.DIV_INST)

        self.instruction.append_argument(ConcreteStackValue(concrete_arg0))
        self.instruction.append_argument(ConcreteStackValue(concrete_arg1))
        self.instruction.return_value = StackValue(return_idx)

        inst_div(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_div_by_zero(self):
        concrete_arg0 = 1
        sym_arg1 = BitVecVal(0, WORD_SIZE)
        sym_arg_idx = 1
        return_idx = 0
        expected = 0

        self.create_instruction(self.DIV_INST)
        self.instruction.append_argument(ConcreteStackValue(concrete_arg0))
        self.state.registers.set(sym_arg_idx, sym_arg1)
        self.instruction.append_argument(StackValue(sym_arg_idx))
        self.instruction.return_value = StackValue(return_idx)

        inst_div(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_div_one_symbolic(self):
        concrete_arg = 5
        sym_arg = BitVec('%2', WORD_SIZE)
        sym_arg_idx = 1
        return_idx = 0
        expected = simplify(UDiv(concrete_arg, sym_arg))

        self.create_instruction(self.DIV_INST)

        self.instruction.append_argument(ConcreteStackValue(concrete_arg))
        self.state.registers.set(sym_arg_idx, sym_arg)
        self.instruction.append_argument(StackValue(sym_arg_idx))
        self.instruction.return_value = StackValue(return_idx)

        inst_div(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ SDIV #####################
    def test_sdiv_two_concrete_values(self):
        concrete_arg0 = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffe
        concrete_arg1 = 2
        return_idx = 0
        expected = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
        self.create_instruction(self.SDIV_INST)

        self.instruction.append_argument(ConcreteStackValue(concrete_arg0))
        self.instruction.append_argument(ConcreteStackValue(concrete_arg1))
        self.instruction.return_value = StackValue(return_idx)

        inst_sdiv(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_sdiv_by_zero(self):
        concrete_arg0 = 1
        sym_arg1 = BitVecVal(0, WORD_SIZE)
        sym_arg_idx = 1
        return_idx = 0
        expected = 0

        self.create_instruction(self.SDIV_INST)
        self.instruction.append_argument(ConcreteStackValue(concrete_arg0))
        self.state.registers.set(sym_arg_idx, sym_arg1)
        self.instruction.append_argument(StackValue(sym_arg_idx))
        self.instruction.return_value = StackValue(return_idx)

        inst_sdiv(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_sdiv_one_symbolic(self):
        concrete_arg = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffe
        sym_arg = BitVec('%2', WORD_SIZE)
        sym_arg_idx = 1
        return_idx = 0
        expected = simplify(concrete_arg / sym_arg)

        self.create_instruction(self.SDIV_INST)
        self.instruction.append_argument(ConcreteStackValue(concrete_arg))
        self.state.registers.set(sym_arg_idx, sym_arg)
        self.instruction.append_argument(StackValue(sym_arg_idx))
        self.instruction.return_value = StackValue(return_idx)

        inst_sdiv(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ MOD #####################
    def test_mod_two_concrete_values(self):
        concrete_arg0 = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
        concrete_arg1 = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffe
        return_idx = 0
        expected = 1
        self.create_instruction(self.MOD_INST)

        self.instruction.append_argument(ConcreteStackValue(concrete_arg0))
        self.instruction.append_argument(ConcreteStackValue(concrete_arg1))
        self.instruction.return_value = StackValue(return_idx)

        inst_mod(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_mod_by_zero(self):
        concrete_arg0 = 10
        sym_arg1 = BitVecVal(0, WORD_SIZE)
        sym_arg_idx = 1
        return_idx = 0
        expected = 0

        self.create_instruction(self.MOD_INST)
        self.instruction.append_argument(ConcreteStackValue(concrete_arg0))
        self.state.registers.set(sym_arg_idx, sym_arg1)
        self.instruction.append_argument(StackValue(sym_arg_idx))
        self.instruction.return_value = StackValue(return_idx)

        inst_mod(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_mod_one_symbolic(self):
        concrete_arg = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffe
        sym_arg = BitVec('%2', WORD_SIZE)
        sym_arg_idx = 1
        return_idx = 0
        expected = simplify(URem(concrete_arg, sym_arg))

        self.create_instruction(self.MOD_INST)
        self.instruction.append_argument(ConcreteStackValue(concrete_arg))
        self.state.registers.set(sym_arg_idx, sym_arg)
        self.instruction.append_argument(StackValue(sym_arg_idx))
        self.instruction.return_value = StackValue(return_idx)

        inst_mod(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ SMOD #####################
    def test_smod_two_concrete_values(self):
        concrete_arg0 = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffb
        concrete_arg1 = 4
        return_idx = 0
        expected = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
        self.create_instruction(self.SMOD_INST)

        self.instruction.append_argument(ConcreteStackValue(concrete_arg0))
        self.instruction.append_argument(ConcreteStackValue(concrete_arg1))
        self.instruction.return_value = StackValue(return_idx)

        inst_smod(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_smod_by_zero(self):
        concrete_arg0 = 10
        sym_arg1 = BitVecVal(0, WORD_SIZE)
        sym_arg_idx = 1
        return_idx = 0
        expected = 0

        self.create_instruction(self.SMOD_INST)
        self.instruction.append_argument(ConcreteStackValue(concrete_arg0))
        self.state.registers.set(sym_arg_idx, sym_arg1)
        self.instruction.append_argument(StackValue(sym_arg_idx))
        self.instruction.return_value = StackValue(return_idx)

        inst_smod(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_smod_one_symbolic(self):
        concrete_arg = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffb
        sym_arg = BitVec('%2', WORD_SIZE)
        sym_arg_idx = 1
        return_idx = 0
        expected = simplify(SRem(concrete_arg, sym_arg))

        self.create_instruction(self.SMOD_INST)
        self.instruction.append_argument(ConcreteStackValue(concrete_arg))
        self.state.registers.set(sym_arg_idx, sym_arg)
        self.instruction.append_argument(StackValue(sym_arg_idx))
        self.instruction.return_value = StackValue(return_idx)

        inst_smod(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ ADDMOD #####################
    def test_addmod_two_concrete_values(self):
        a = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffb
        b = 0x3ffffc0000000000000000000000000000000000000000000000000000000004
        n = 5
        return_idx = 0
        expected = BitVecVal(0, WORD_SIZE)
        self.create_instruction(self.ADDMOD_INST)

        self.instruction.append_argument(ConcreteStackValue(a))
        self.instruction.append_argument(ConcreteStackValue(b))
        self.instruction.append_argument(ConcreteStackValue(n))
        self.instruction.return_value = StackValue(return_idx)

        inst_addmod(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_addmod_by_zero(self):
        a = 10
        b = 5
        sym_n = BitVecVal(0, WORD_SIZE)
        sym_n_idx = 1
        return_idx = 0
        expected = 0

        self.create_instruction(self.ADDMOD_INST)
        self.instruction.append_argument(ConcreteStackValue(a))
        self.instruction.append_argument(ConcreteStackValue(b))
        self.state.registers.set(sym_n_idx, sym_n)
        self.instruction.append_argument(StackValue(sym_n_idx))
        self.instruction.return_value = StackValue(return_idx)

        inst_addmod(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_addmod_one_symbolic(self):
        a = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffb
        sym_b = BitVec('%2', WORD_SIZE)
        sym_b_idx = 1
        n = 5
        sym_n = BitVecVal(5, WORD_SIZE)
        return_idx = 0
        expected = simplify(URem(URem(a, sym_n) + URem(sym_b, sym_n), sym_n))

        self.create_instruction(self.ADDMOD_INST)
        self.instruction.append_argument(ConcreteStackValue(a))
        self.state.registers.set(sym_b_idx, sym_b)
        self.instruction.append_argument(StackValue(sym_b_idx))
        self.instruction.append_argument(ConcreteStackValue(n))
        self.instruction.return_value = StackValue(return_idx)

        inst_addmod(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ MULMOD #####################
    def test_mulmod_two_concrete_values(self):
        a = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffb
        b = 0x3ffffc0000000000000000000000000000000000000000000000000000000004
        n = 5
        return_idx = 0
        expected = BitVecVal(4, WORD_SIZE)
        self.create_instruction(self.MULMOD_INST)

        self.instruction.append_argument(ConcreteStackValue(a))
        self.instruction.append_argument(ConcreteStackValue(b))
        self.instruction.append_argument(ConcreteStackValue(n))
        self.instruction.return_value = StackValue(return_idx)

        inst_mulmod(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_mulmod_by_zero(self):
        a = 10
        b = 5
        sym_n = BitVecVal(0, WORD_SIZE)
        sym_n_idx = 1
        return_idx = 0
        expected = 0

        self.create_instruction(self.MULMOD_INST)
        self.instruction.append_argument(ConcreteStackValue(a))
        self.instruction.append_argument(ConcreteStackValue(b))
        self.state.registers.set(sym_n_idx, sym_n)
        self.instruction.append_argument(StackValue(sym_n_idx))
        self.instruction.return_value = StackValue(return_idx)

        inst_mulmod(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_mulmod_one_symbolic(self):
        a = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffb
        sym_b = BitVec('%2', WORD_SIZE)
        sym_b_idx = 1
        n = 5
        sym_n = BitVecVal(5, WORD_SIZE)
        return_idx = 0
        expected = simplify(URem(URem(a, sym_n) * URem(sym_b, sym_n), sym_n))

        self.create_instruction(self.MULMOD_INST)
        self.instruction.append_argument(ConcreteStackValue(a))
        self.state.registers.set(sym_b_idx, sym_b)
        self.instruction.append_argument(StackValue(sym_b_idx))
        self.instruction.append_argument(ConcreteStackValue(n))
        self.instruction.return_value = StackValue(return_idx)

        inst_mulmod(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ EXP #####################
    def test_exp_two_concrete_values(self):
        a = 0x2000000000000000000000000000000ff
        b = 2
        return_idx = 0
        expected = 0x3fc0000000000000000000000000000fe01
        self.create_instruction(self.EXP_INST)

        self.instruction.append_argument(ConcreteStackValue(a))
        self.instruction.append_argument(ConcreteStackValue(b))
        self.instruction.return_value = StackValue(return_idx)

        inst_exp(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_exp_zero_base(self):
        a = 0
        b = 15
        return_idx = 0
        expected = 0

        self.create_instruction(self.EXP_INST)
        self.instruction.append_argument(ConcreteStackValue(a))
        self.instruction.append_argument(ConcreteStackValue(b))
        self.instruction.return_value = StackValue(return_idx)

        inst_exp(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_exp_zero_exponent(self):
        a = 15
        b = 0
        return_idx = 0
        expected = 1

        self.create_instruction(self.EXP_INST)
        self.instruction.append_argument(ConcreteStackValue(a))
        self.instruction.append_argument(ConcreteStackValue(b))
        self.instruction.return_value = StackValue(return_idx)

        inst_exp(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_exp_base_exponent_zero(self):
        a = 0
        b = 0
        return_idx = 0
        expected = 1

        self.create_instruction(self.EXP_INST)
        self.instruction.append_argument(ConcreteStackValue(a))
        self.instruction.append_argument(ConcreteStackValue(b))
        self.instruction.return_value = StackValue(return_idx)

        inst_exp(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_exp_one_symbolic(self):
        a = 15
        sym_b = BitVec('%2', WORD_SIZE)
        sym_b_idx = 1
        return_idx = 0
        expected = BitVec(str(return_idx), WORD_SIZE)

        self.create_instruction(self.EXP_INST)
        self.instruction.append_argument(ConcreteStackValue(a))
        self.state.registers.set(sym_b_idx, sym_b)
        self.instruction.append_argument(StackValue(sym_b_idx))
        self.instruction.return_value = StackValue(return_idx)

        inst_exp(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ SIGNEXTEND #####################
    def test_signextend_one_bit_concrete_values(self):
        a = 0
        b = 0x8181
        return_idx = 0
        expected = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff81
        self.create_instruction(self.SIGNEXTEND_INST)

        self.instruction.append_argument(ConcreteStackValue(a))
        self.instruction.append_argument(ConcreteStackValue(b))
        self.instruction.return_value = StackValue(return_idx)

        inst_signextend(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_signextend_zero_bit_concrete_values(self):
        a = 0
        b = 0x4141
        return_idx = 0
        expected = 0x41

        self.create_instruction(self.SIGNEXTEND_INST)
        self.instruction.append_argument(ConcreteStackValue(a))
        self.instruction.append_argument(ConcreteStackValue(b))
        self.instruction.return_value = StackValue(return_idx)

        inst_signextend(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_signextend_more_than_32_bits(self):
        a = 32
        b = 0x8181818181000000000000000000000000000000000000000000000000000000
        return_idx = 0
        expected = 0x8181818181000000000000000000000000000000000000000000000000000000

        self.create_instruction(self.SIGNEXTEND_INST)
        self.instruction.append_argument(ConcreteStackValue(a))
        self.instruction.append_argument(ConcreteStackValue(b))
        self.instruction.return_value = StackValue(return_idx)

        inst_signextend(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_signextend_symbolic_value(self):
        a = 1
        sym_b = BitVec('%2', WORD_SIZE)
        sym_b_idx = 1
        return_idx = 0
        expected = BitVec(str(return_idx), WORD_SIZE)

        self.create_instruction(self.SIGNEXTEND_INST)
        self.instruction.append_argument(ConcreteStackValue(a))
        self.state.registers.set(sym_b_idx, sym_b)
        self.instruction.append_argument(StackValue(sym_b_idx))
        self.instruction.return_value = StackValue(return_idx)

        inst_signextend(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ SHL #####################
    def test_shl_concrete_values(self):
        shift = 0xff
        value = 1
        return_idx = 0
        expected = 0x8000000000000000000000000000000000000000000000000000000000000000
        self.create_instruction(self.SHL_INST)

        self.instruction.append_argument(ConcreteStackValue(shift))
        self.instruction.append_argument(ConcreteStackValue(value))
        self.instruction.return_value = StackValue(return_idx)

        inst_shl(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_shl_more_than_255_bits(self):
        shift = 0x100
        value = 0xff
        return_idx = 0
        expected = 0

        self.create_instruction(self.SHL_INST)
        self.instruction.append_argument(ConcreteStackValue(shift))
        self.instruction.append_argument(ConcreteStackValue(value))
        self.instruction.return_value = StackValue(return_idx)

        inst_shl(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_shl_zero_shift(self):
        shift = 0
        value = 0x4141
        return_idx = 0
        expected = 0x4141

        self.create_instruction(self.SHL_INST)
        self.instruction.append_argument(ConcreteStackValue(shift))
        self.instruction.append_argument(ConcreteStackValue(value))
        self.instruction.return_value = StackValue(return_idx)

        inst_shl(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_shl_symbolic_value(self):
        shift = 1
        sym_value = BitVec('%2', WORD_SIZE)
        sym_value_idx = 1
        return_idx = 0
        expected = simplify(sym_value << shift)

        self.create_instruction(self.SHL_INST)
        self.instruction.append_argument(ConcreteStackValue(shift))
        self.state.registers.set(sym_value_idx, sym_value)
        self.instruction.append_argument(StackValue(sym_value_idx))
        self.instruction.return_value = StackValue(return_idx)

        inst_shl(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ SHR #####################
    def test_shr_concrete_values(self):
        shift = 1
        value = 0xff00000000000000000000000000000000000000000000000000000000000000
        return_idx = 0
        expected = 0x7f80000000000000000000000000000000000000000000000000000000000000
        self.create_instruction(self.SHR_INST)

        self.instruction.append_argument(ConcreteStackValue(shift))
        self.instruction.append_argument(ConcreteStackValue(value))
        self.instruction.return_value = StackValue(return_idx)

        inst_shr(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_shr_more_than_255_bits(self):
        shift = 0x100
        value = 0xff00000000000000000000000000000000000000000000000000000000000000
        return_idx = 0
        expected = 0

        self.create_instruction(self.SHR_INST)
        self.instruction.append_argument(ConcreteStackValue(shift))
        self.instruction.append_argument(ConcreteStackValue(value))
        self.instruction.return_value = StackValue(return_idx)

        inst_shr(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_shr_zero_shift(self):
        shift = 0
        value = 0x4141
        return_idx = 0
        expected = 0x4141

        self.create_instruction(self.SHR_INST)
        self.instruction.append_argument(ConcreteStackValue(shift))
        self.instruction.append_argument(ConcreteStackValue(value))
        self.instruction.return_value = StackValue(return_idx)

        inst_shr(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_shr_symbolic_value(self):
        shift = 1
        sym_value = BitVec('%2', WORD_SIZE)
        sym_value_idx = 1
        return_idx = 0
        expected = simplify(LShR(sym_value, shift))

        self.create_instruction(self.SHR_INST)
        self.instruction.append_argument(ConcreteStackValue(shift))
        self.state.registers.set(sym_value_idx, sym_value)
        self.instruction.append_argument(StackValue(sym_value_idx))
        self.instruction.return_value = StackValue(return_idx)

        inst_shr(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ SAR #####################
    def test_sar_concrete_values(self):
        shift = 0xf0
        value = 0xff00000000000000000000000000000000000000000000000000000000000000
        return_idx = 0
        expected = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff00
        self.create_instruction(self.SAR_INST)

        self.instruction.append_argument(ConcreteStackValue(shift))
        self.instruction.append_argument(ConcreteStackValue(value))
        self.instruction.return_value = StackValue(return_idx)

        inst_sar(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_sar_shift_more_than_255_bits_negative_value(self):
        shift = 0x100
        value = 0xff00000000000000000000000000000000000000000000000000000000000000
        return_idx = 0
        expected = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff

        self.create_instruction(self.SAR_INST)
        self.instruction.append_argument(ConcreteStackValue(shift))
        self.instruction.append_argument(ConcreteStackValue(value))
        self.instruction.return_value = StackValue(return_idx)

        inst_sar(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_sar_shift_more_than_255_bits_positive_value(self):
        shift = 0x100
        value = 0x7fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
        return_idx = 0
        expected = 0

        self.create_instruction(self.SAR_INST)
        self.instruction.append_argument(ConcreteStackValue(shift))
        self.instruction.append_argument(ConcreteStackValue(value))
        self.instruction.return_value = StackValue(return_idx)

        inst_sar(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_sar_zero_shift(self):
        shift = 0
        value = 0x4141
        return_idx = 0
        expected = 0x4141

        self.create_instruction(self.SAR_INST)
        self.instruction.append_argument(ConcreteStackValue(shift))
        self.instruction.append_argument(ConcreteStackValue(value))
        self.instruction.return_value = StackValue(return_idx)

        inst_sar(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_sar_symbolic_value(self):
        shift = 1
        sym_value = BitVec('%2', WORD_SIZE)
        sym_value_idx = 1
        return_idx = 0
        expected = simplify(sym_value >> shift)

        self.create_instruction(self.SAR_INST)
        self.instruction.append_argument(ConcreteStackValue(shift))
        self.state.registers.set(sym_value_idx, sym_value)
        self.instruction.append_argument(StackValue(sym_value_idx))
        self.instruction.return_value = StackValue(return_idx)

        inst_sar(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
