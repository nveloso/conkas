import unittest

from z3 import Extract

from rattle import EVMAsm, SSABasicBlock, SSAFunction, StackValue
from sym_exec.instructions.closures import *
from sym_exec.state import State
from sym_exec.utils import *


class TestClosures(unittest.TestCase):
    CREATE_INST = 'CREATE'
    CALL_INST = 'CALL'
    CALLCODE_INST = 'CALLCODE'
    RETURN_INST = 'RETURN'
    DELEGATECALL_INST = 'DELEGATECALL'
    CREATE2_INST = 'CREATE2'
    STATICCALL_INST = 'STATICCALL'
    REVERT_INST = 'REVERT'
    INVALID_INST = 'INVALID'
    SELFDESTRUCT_INST = 'SELFDESTRUCT'

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

    ################ CREATE #####################
    def test_create(self):
        value = 1
        offset = 0
        length = 4
        return_idx = 0
        expected = BitVec('0', WORD_SIZE)

        self.create_instruction(self.CREATE_INST)
        self.instruction.append_argument(ConcreteStackValue(value))
        self.instruction.append_argument(ConcreteStackValue(offset))
        self.instruction.append_argument(ConcreteStackValue(length))
        self.instruction.return_value = StackValue(return_idx)

        inst_create(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ CALL #####################
    def test_call_without_return_data(self):
        gas = 0
        addr = 0
        value = 0
        args_offset = 0
        args_length = 0
        ret_offset = 0
        ret_length = 0
        return_idx = 0
        expected = BitVec('0', WORD_SIZE)

        self.create_instruction(self.CALL_INST)
        self.instruction.append_argument(ConcreteStackValue(gas))
        self.instruction.append_argument(ConcreteStackValue(addr))
        self.instruction.append_argument(ConcreteStackValue(value))
        self.instruction.append_argument(ConcreteStackValue(args_offset))
        self.instruction.append_argument(ConcreteStackValue(args_length))
        self.instruction.append_argument(ConcreteStackValue(ret_offset))
        self.instruction.append_argument(ConcreteStackValue(ret_length))
        self.instruction.return_value = StackValue(return_idx)

        inst_call(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)
        self.assertEqual(0, self.state.memory.load(ret_offset, ret_length))

    def test_call_with_return_data(self):
        gas = 0
        addr = 0
        value = 0
        args_offset = 0
        args_length = 0
        ret_offset = 0
        ret_length = 10
        return_idx = 0
        expected = BitVec('0', WORD_SIZE)

        self.create_instruction(self.CALL_INST)
        self.instruction.append_argument(ConcreteStackValue(gas))
        self.instruction.append_argument(ConcreteStackValue(addr))
        self.instruction.append_argument(ConcreteStackValue(value))
        self.instruction.append_argument(ConcreteStackValue(args_offset))
        self.instruction.append_argument(ConcreteStackValue(args_length))
        self.instruction.append_argument(ConcreteStackValue(ret_offset))
        self.instruction.append_argument(ConcreteStackValue(ret_length))
        self.instruction.return_value = StackValue(return_idx)

        inst_call(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)
        self.assertEqual(BitVec('ret_code_0', 80), self.state.memory.load(ret_offset, ret_length))

    def test_call_with_return_offset_symbolic(self):
        gas = 0
        addr = 0
        value = 0
        args_offset = 0
        args_length = 0
        ret_offset = BitVec('ret_offset', WORD_SIZE)
        ret_offset_idx = 1
        ret_length = 10
        return_idx = 0
        expected = BitVec('0', WORD_SIZE)

        self.create_instruction(self.CALL_INST)
        self.instruction.append_argument(ConcreteStackValue(gas))
        self.instruction.append_argument(ConcreteStackValue(addr))
        self.instruction.append_argument(ConcreteStackValue(value))
        self.instruction.append_argument(ConcreteStackValue(args_offset))
        self.instruction.append_argument(ConcreteStackValue(args_length))
        self.state.registers.set(ret_offset_idx, ret_offset)
        self.instruction.append_argument(StackValue(ret_offset_idx))
        self.instruction.append_argument(ConcreteStackValue(ret_length))
        self.instruction.return_value = StackValue(return_idx)

        inst_call(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)
        self.assertEqual(0, self.state.memory.size)

    ################ CALLCODE #####################
    def test_callcode_without_return_data(self):
        gas = 0
        addr = 0
        value = 0
        args_offset = 0
        args_length = 0
        ret_offset = 0
        ret_length = 0
        return_idx = 0
        expected = BitVec('0', WORD_SIZE)

        self.create_instruction(self.CALLCODE_INST)
        self.instruction.append_argument(ConcreteStackValue(gas))
        self.instruction.append_argument(ConcreteStackValue(addr))
        self.instruction.append_argument(ConcreteStackValue(value))
        self.instruction.append_argument(ConcreteStackValue(args_offset))
        self.instruction.append_argument(ConcreteStackValue(args_length))
        self.instruction.append_argument(ConcreteStackValue(ret_offset))
        self.instruction.append_argument(ConcreteStackValue(ret_length))
        self.instruction.return_value = StackValue(return_idx)

        inst_callcode(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)
        self.assertEqual(0, self.state.memory.load(ret_offset, ret_length))

    def test_callcode_with_return_data(self):
        gas = 0
        addr = 0
        value = 0
        args_offset = 0
        args_length = 0
        ret_offset = 0
        ret_length = 10
        return_idx = 0
        expected = BitVec('0', WORD_SIZE)

        self.create_instruction(self.CALLCODE_INST)
        self.instruction.append_argument(ConcreteStackValue(gas))
        self.instruction.append_argument(ConcreteStackValue(addr))
        self.instruction.append_argument(ConcreteStackValue(value))
        self.instruction.append_argument(ConcreteStackValue(args_offset))
        self.instruction.append_argument(ConcreteStackValue(args_length))
        self.instruction.append_argument(ConcreteStackValue(ret_offset))
        self.instruction.append_argument(ConcreteStackValue(ret_length))
        self.instruction.return_value = StackValue(return_idx)

        inst_callcode(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)
        self.assertEqual(BitVec('ret_code_0', 80), self.state.memory.load(ret_offset, ret_length))

    def test_callcode_with_return_offset_symbolic(self):
        gas = 0
        addr = 0
        value = 0
        args_offset = 0
        args_length = 0
        ret_offset = BitVec('ret_offset', WORD_SIZE)
        ret_offset_idx = 1
        ret_length = 10
        return_idx = 0
        expected = BitVec('0', WORD_SIZE)

        self.create_instruction(self.CALLCODE_INST)
        self.instruction.append_argument(ConcreteStackValue(gas))
        self.instruction.append_argument(ConcreteStackValue(addr))
        self.instruction.append_argument(ConcreteStackValue(value))
        self.instruction.append_argument(ConcreteStackValue(args_offset))
        self.instruction.append_argument(ConcreteStackValue(args_length))
        self.state.registers.set(ret_offset_idx, ret_offset)
        self.instruction.append_argument(StackValue(ret_offset_idx))
        self.instruction.append_argument(ConcreteStackValue(ret_length))
        self.instruction.return_value = StackValue(return_idx)

        inst_callcode(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)
        self.assertEqual(0, self.state.memory.size)

    ################ RETURN #####################
    def test_return_concrete_values(self):
        offset = 0
        length = 2
        mem = self.state.memory
        mem.extend(0, 4)
        mem.store(0, 0xcafebabe, 4)
        expected = 0xcafe

        self.create_instruction(self.RETURN_INST)
        self.instruction.append_argument(ConcreteStackValue(offset))
        self.instruction.append_argument(ConcreteStackValue(length))

        inst_return(self.instruction, self.state)
        actual = self.state.return_data

        self.assertEqual(expected, actual)

    def test_return_symbolic_length(self):
        offset = 0
        length = BitVec('length', WORD_SIZE)
        length_idx = 0
        expected = BitVec('ret_data', WORD_SIZE)

        self.create_instruction(self.RETURN_INST)
        self.instruction.append_argument(ConcreteStackValue(offset))
        self.state.registers.set(length_idx, length)
        self.instruction.append_argument(StackValue(length_idx))

        inst_return(self.instruction, self.state)
        actual = self.state.return_data

        self.assertEqual(expected, actual)

    def test_return_symbolic_offset(self):
        offset = BitVec('offset', WORD_SIZE)
        offset_idx = 0
        length = 2
        mem = self.state.memory
        value = BitVec('value', 32)
        mem.store(offset, value, 4)
        expected = Extract(31, 16, value)

        self.create_instruction(self.RETURN_INST)
        self.state.registers.set(offset_idx, offset)
        self.instruction.append_argument(StackValue(offset_idx))
        self.instruction.append_argument(ConcreteStackValue(length))

        inst_return(self.instruction, self.state)
        actual = self.state.return_data

        self.assertEqual(expected, actual)

    ################ DELEGATECALL #####################
    def test_delegatecall_without_return_data(self):
        gas = 0
        addr = 0
        args_offset = 0
        args_length = 0
        ret_offset = 0
        ret_length = 0
        return_idx = 0
        expected = BitVec('0', WORD_SIZE)

        self.create_instruction(self.DELEGATECALL_INST)
        self.instruction.append_argument(ConcreteStackValue(gas))
        self.instruction.append_argument(ConcreteStackValue(addr))
        self.instruction.append_argument(ConcreteStackValue(args_offset))
        self.instruction.append_argument(ConcreteStackValue(args_length))
        self.instruction.append_argument(ConcreteStackValue(ret_offset))
        self.instruction.append_argument(ConcreteStackValue(ret_length))
        self.instruction.return_value = StackValue(return_idx)

        inst_delegatecall(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)
        self.assertEqual(0, self.state.memory.load(ret_offset, ret_length))

    def test_delegatecall_with_return_data(self):
        gas = 0
        addr = 0
        args_offset = 0
        args_length = 0
        ret_offset = 0
        ret_length = 10
        return_idx = 0
        expected = BitVec('0', WORD_SIZE)

        self.create_instruction(self.DELEGATECALL_INST)
        self.instruction.append_argument(ConcreteStackValue(gas))
        self.instruction.append_argument(ConcreteStackValue(addr))
        self.instruction.append_argument(ConcreteStackValue(args_offset))
        self.instruction.append_argument(ConcreteStackValue(args_length))
        self.instruction.append_argument(ConcreteStackValue(ret_offset))
        self.instruction.append_argument(ConcreteStackValue(ret_length))
        self.instruction.return_value = StackValue(return_idx)

        inst_delegatecall(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)
        self.assertEqual(BitVec('ret_code_0', 80), self.state.memory.load(ret_offset, ret_length))

    def test_delegatecall_with_return_offset_symbolic(self):
        gas = 0
        addr = 0
        args_offset = 0
        args_length = 0
        ret_offset = BitVec('ret_offset', WORD_SIZE)
        ret_offset_idx = 1
        ret_length = 10
        return_idx = 0
        expected = BitVec('0', WORD_SIZE)

        self.create_instruction(self.DELEGATECALL_INST)
        self.instruction.append_argument(ConcreteStackValue(gas))
        self.instruction.append_argument(ConcreteStackValue(addr))
        self.instruction.append_argument(ConcreteStackValue(args_offset))
        self.instruction.append_argument(ConcreteStackValue(args_length))
        self.state.registers.set(ret_offset_idx, ret_offset)
        self.instruction.append_argument(StackValue(ret_offset_idx))
        self.instruction.append_argument(ConcreteStackValue(ret_length))
        self.instruction.return_value = StackValue(return_idx)

        inst_delegatecall(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)
        self.assertEqual(0, self.state.memory.size)

    ################ CREATE2 #####################
    # TODO: uncommented when pyevmasm lib merge my PR
    # def test_create2(self):
    #     value = 0
    #     offset = 1
    #     length = 2
    #     salt = 3
    #     return_idx = 0
    #     expected = BitVec('0', WORD_SIZE)
    #
    #     self.create_instruction(self.CREATE2_INST)
    #     self.instruction.append_argument(ConcreteStackValue(value))
    #     self.instruction.append_argument(ConcreteStackValue(offset))
    #     self.instruction.append_argument(ConcreteStackValue(length))
    #     self.instruction.append_argument(ConcreteStackValue(salt))
    #     self.instruction.return_value = StackValue(return_idx)
    #
    #     inst_create2(self.instruction, self.state)
    #     actual = self.state.registers.get(return_idx)
    #
    #     self.assertEqual(expected, actual)

    ################ STATICCALL #####################
    def test_staticcall_without_return_data(self):
        gas = 0
        addr = 0
        args_offset = 0
        args_length = 0
        ret_offset = 0
        ret_length = 0
        return_idx = 0
        expected = BitVec('0', WORD_SIZE)

        self.create_instruction(self.STATICCALL_INST)
        self.instruction.append_argument(ConcreteStackValue(gas))
        self.instruction.append_argument(ConcreteStackValue(addr))
        self.instruction.append_argument(ConcreteStackValue(args_offset))
        self.instruction.append_argument(ConcreteStackValue(args_length))
        self.instruction.append_argument(ConcreteStackValue(ret_offset))
        self.instruction.append_argument(ConcreteStackValue(ret_length))
        self.instruction.return_value = StackValue(return_idx)

        inst_staticcall(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)
        self.assertEqual(0, self.state.memory.load(ret_offset, ret_length))

    def test_staticcall_with_return_data(self):
        gas = 0
        addr = 0
        args_offset = 0
        args_length = 0
        ret_offset = 0
        ret_length = 10
        return_idx = 0
        expected = BitVec('0', WORD_SIZE)

        self.create_instruction(self.STATICCALL_INST)
        self.instruction.append_argument(ConcreteStackValue(gas))
        self.instruction.append_argument(ConcreteStackValue(addr))
        self.instruction.append_argument(ConcreteStackValue(args_offset))
        self.instruction.append_argument(ConcreteStackValue(args_length))
        self.instruction.append_argument(ConcreteStackValue(ret_offset))
        self.instruction.append_argument(ConcreteStackValue(ret_length))
        self.instruction.return_value = StackValue(return_idx)

        inst_staticcall(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)
        self.assertEqual(BitVec('ret_code_0', 80), self.state.memory.load(ret_offset, ret_length))

    def test_staticcall_with_return_offset_symbolic(self):
        gas = 0
        addr = 0
        args_offset = 0
        args_length = 0
        ret_offset = BitVec('ret_offset', WORD_SIZE)
        ret_offset_idx = 1
        ret_length = 10
        return_idx = 0
        expected = BitVec('0', WORD_SIZE)

        self.create_instruction(self.STATICCALL_INST)
        self.instruction.append_argument(ConcreteStackValue(gas))
        self.instruction.append_argument(ConcreteStackValue(addr))
        self.instruction.append_argument(ConcreteStackValue(args_offset))
        self.instruction.append_argument(ConcreteStackValue(args_length))
        self.state.registers.set(ret_offset_idx, ret_offset)
        self.instruction.append_argument(StackValue(ret_offset_idx))
        self.instruction.append_argument(ConcreteStackValue(ret_length))
        self.instruction.return_value = StackValue(return_idx)

        inst_staticcall(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)
        self.assertEqual(0, self.state.memory.size)

    ################ REVERT #####################
    def test_revert_concrete_values(self):
        offset = 0
        length = 2
        mem = self.state.memory
        mem.extend(0, 4)
        mem.store(0, 0xcafebabe, 4)
        expected = 0xcafe

        self.create_instruction(self.REVERT_INST)
        self.instruction.append_argument(ConcreteStackValue(offset))
        self.instruction.append_argument(ConcreteStackValue(length))

        inst_revert(self.instruction, self.state)
        actual = self.state.return_data

        self.assertEqual(expected, actual)
        self.assertTrue(self.state.reverted)

    def test_revert_symbolic_length(self):
        offset = 0
        length = BitVec('length', WORD_SIZE)
        length_idx = 0
        expected = BitVec('rev_data', WORD_SIZE)

        self.create_instruction(self.REVERT_INST)
        self.instruction.append_argument(ConcreteStackValue(offset))
        self.state.registers.set(length_idx, length)
        self.instruction.append_argument(StackValue(length_idx))

        inst_revert(self.instruction, self.state)
        actual = self.state.return_data

        self.assertEqual(expected, actual)
        self.assertTrue(self.state.reverted)

    def test_revert_symbolic_offset(self):
        offset = BitVec('offset', WORD_SIZE)
        offset_idx = 0
        length = 2
        mem = self.state.memory
        value = BitVec('value', 32)
        mem.store(offset, value, 4)
        expected = Extract(31, 16, value)

        self.create_instruction(self.REVERT_INST)
        self.state.registers.set(offset_idx, offset)
        self.instruction.append_argument(StackValue(offset_idx))
        self.instruction.append_argument(ConcreteStackValue(length))

        inst_revert(self.instruction, self.state)
        actual = self.state.return_data

        self.assertEqual(expected, actual)
        self.assertTrue(self.state.reverted)

    ################ INVALID #####################
    def test_invalid(self):
        self.create_instruction(self.INVALID_INST)

        inst_invalid(self.instruction, self.state)

        self.assertTrue(self.state.invalid)

    ################ SELFDESTRUCT #####################
    def test_selfdestruct(self):
        addr = 0

        self.create_instruction(self.SELFDESTRUCT_INST)
        self.instruction.append_argument(ConcreteStackValue(addr))

        inst_selfdestruct(self.instruction, self.state)

        self.assertTrue(self.state.destructed)
