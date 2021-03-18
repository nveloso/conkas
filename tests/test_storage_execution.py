import unittest

from z3 import Extract, BitVecVal, If

from rattle import EVMAsm, SSABasicBlock, SSAFunction, StackValue
from sym_exec.instructions.storage_execution import *
from sym_exec.state import State
from sym_exec.utils import *


class TestStorageExecution(unittest.TestCase):
    MLOAD_INST = 'MLOAD'
    MSTORE_INST = 'MSTORE'
    MSTORE8_INST = 'MSTORE8'
    SLOAD_INST = 'SLOAD'
    SSTORE_INST = 'SSTORE'
    JUMP_INST = 'JUMP'
    JUMPI_INST = 'JUMPI'
    PC_INST = 'GETPC'
    MSIZE_INST = 'MSIZE'
    GAS_INST = 'GAS'
    JUMPDEST_INST = 'JUMPDEST'

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

    ################ MLOAD #####################
    def test_mload_all_concrete_values(self):
        offset = 0
        expected = 0xdeadbeefcafebabe
        self.state.memory.extend(offset, 32)
        self.state.memory.store(offset, expected)
        return_idx = 0

        self.create_instruction(self.MLOAD_INST)
        self.instruction.append_argument(ConcreteStackValue(offset))
        self.instruction.return_value = StackValue(return_idx)

        inst_mload(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_mload_uninitialized_region(self):
        offset = 2
        expected = 0xdeadbeefcafebabe0000
        return_idx = 0
        self.state.memory.extend(0, 32)
        self.state.memory.store(0, 0xdeadbeefcafebabe)

        self.create_instruction(self.MLOAD_INST)
        self.instruction.append_argument(ConcreteStackValue(offset))
        self.instruction.return_value = StackValue(return_idx)

        inst_mload(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_mload_symbolic_uninitialized_region(self):
        offset = BitVec('2', WORD_SIZE)
        offset_idx = 1
        return_idx = 0
        expected = 0

        self.create_instruction(self.MLOAD_INST)
        self.state.registers.set(offset_idx, offset)
        self.instruction.append_argument(StackValue(offset_idx))
        self.instruction.return_value = StackValue(return_idx)

        inst_mload(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_mload_symbolic_offset_store_concrete_value(self):
        offset = BitVec('2', WORD_SIZE)
        offset_idx = 1
        return_idx = 0
        expected = 0xdeadbeefcafebabe
        self.state.memory.store(offset, expected)

        self.create_instruction(self.MLOAD_INST)
        self.state.registers.set(offset_idx, offset)
        self.instruction.append_argument(StackValue(offset_idx))
        self.instruction.return_value = StackValue(return_idx)

        inst_mload(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ MSTORE #####################
    def test_mstore_all_concrete_values(self):
        offset = 0
        value = 0xdeadbeefcafebabe
        expected = 0xdeadbeefcafebabe

        self.create_instruction(self.MSTORE_INST)
        self.instruction.append_argument(ConcreteStackValue(offset))
        self.instruction.append_argument(ConcreteStackValue(value))

        inst_mstore(self.instruction, self.state)
        actual = self.state.memory.load(offset, 32)

        self.assertEqual(expected, actual)

    def test_mstore_misaligned(self):
        offset = 2
        value = 0xdeadbeefcafebabe
        expected = 0xdeadbeefcafebabe

        self.create_instruction(self.MSTORE_INST)
        self.instruction.append_argument(ConcreteStackValue(offset))
        self.instruction.append_argument(ConcreteStackValue(value))

        inst_mstore(self.instruction, self.state)
        actual = self.state.memory.load(offset, 32)

        self.assertEqual(expected, actual)

    def test_mstore_symbolic_offset_store_concrete_value(self):
        offset = BitVec('2', WORD_SIZE)
        offset_idx = 1
        value = 0xdeadbeefcafebabe
        expected = 0xdeadbeefcafebabe

        self.create_instruction(self.MSTORE_INST)
        self.state.registers.set(offset_idx, offset)
        self.instruction.append_argument(StackValue(offset_idx))
        self.instruction.append_argument(ConcreteStackValue(value))

        inst_mstore(self.instruction, self.state)
        actual = self.state.memory.load(offset, 32)

        self.assertEqual(expected, actual)

    def test_mstore_symbolic_offset_store_symbolic_value(self):
        offset = BitVec('2', WORD_SIZE)
        offset_idx = 1
        value = BitVec('3', WORD_SIZE)
        value_idx = 2
        expected = value

        self.create_instruction(self.MSTORE_INST)
        self.state.registers.set(offset_idx, offset)
        self.instruction.append_argument(StackValue(offset_idx))
        self.state.registers.set(value_idx, value)
        self.instruction.append_argument(StackValue(value_idx))

        inst_mstore(self.instruction, self.state)
        actual = self.state.memory.load(offset, 32)

        self.assertEqual(expected, actual)

    ################ MSTORE8 #####################
    def test_mstore8_all_concrete_values(self):
        offset = 0
        value = 0xbe
        expected = 0xbe

        self.create_instruction(self.MSTORE8_INST)
        self.instruction.append_argument(ConcreteStackValue(offset))
        self.instruction.append_argument(ConcreteStackValue(value))

        inst_mstore8(self.instruction, self.state)
        actual = self.state.memory.load(offset, 1)

        self.assertEqual(expected, actual)

    def test_mstore8_symbolic_offset_store_concrete_value(self):
        offset = BitVec('2', WORD_SIZE)
        offset_idx = 1
        value = 0xdeadbeefcafebabe
        expected = 0xbe

        self.create_instruction(self.MSTORE8_INST)
        self.state.registers.set(offset_idx, offset)
        self.instruction.append_argument(StackValue(offset_idx))
        self.instruction.append_argument(ConcreteStackValue(value))

        inst_mstore8(self.instruction, self.state)
        actual = self.state.memory.load(offset, 1)

        self.assertEqual(expected, actual)

    def test_mstore8_symbolic_offset_store_symbolic_value(self):
        offset = BitVec('2', WORD_SIZE)
        offset_idx = 1
        value = BitVec('3', WORD_SIZE)
        value_idx = 2
        expected = Extract(255, 248, value)

        self.create_instruction(self.MSTORE8_INST)
        self.state.registers.set(offset_idx, offset)
        self.instruction.append_argument(StackValue(offset_idx))
        self.state.registers.set(value_idx, value)
        self.instruction.append_argument(StackValue(value_idx))

        inst_mstore8(self.instruction, self.state)
        actual = self.state.memory.load(offset, 1)

        self.assertEqual(expected, actual)

    ################ SLOAD #####################
    def test_sload_concrete_unknown_key(self):
        key = 0
        return_idx = 0
        expected = BitVec('storage,0,conc', WORD_SIZE)

        self.create_instruction(self.SLOAD_INST)
        self.instruction.append_argument(ConcreteStackValue(key))
        self.instruction.return_value = StackValue(return_idx)

        inst_sload(self.instruction, self.state)
        actual_register = self.state.registers.get(return_idx)
        actual_storage = self.state.storage.get(return_idx)

        self.assertEqual(expected, actual_register)
        self.assertEqual(expected, actual_storage)

    def test_sload_concrete_known_key(self):
        key = 0
        return_idx = 0
        expected = 0xcafebabe
        self.state.storage.set(0, 0xcafebabe)

        self.create_instruction(self.SLOAD_INST)
        self.instruction.append_argument(ConcreteStackValue(key))
        self.instruction.return_value = StackValue(return_idx)

        inst_sload(self.instruction, self.state)
        actual_register = self.state.registers.get(return_idx)
        actual_storage = self.state.storage.get(return_idx)

        self.assertEqual(expected, actual_register)
        self.assertEqual(expected, actual_storage)

    def test_sload_symbolic_unknown_key(self):
        key = BitVec('key', WORD_SIZE)
        key_idx = 1
        return_idx = 0
        expected = BitVec('storage,1,sym', WORD_SIZE)

        self.create_instruction(self.SLOAD_INST)
        self.state.registers.set(key_idx, key)
        self.instruction.append_argument(StackValue(key_idx))
        self.instruction.return_value = StackValue(return_idx)

        inst_sload(self.instruction, self.state)
        actual_register = self.state.registers.get(return_idx)
        actual_storage = self.state.storage.get(key)

        self.assertEqual(expected, actual_register)
        self.assertEqual(expected, actual_storage)

    def test_sload_symbolic_known_key(self):
        key = BitVec('key', WORD_SIZE)
        key_idx = 1
        return_idx = 0
        expected = 0xcafebabe
        self.state.storage.set(key, 0xcafebabe)

        self.create_instruction(self.SLOAD_INST)
        self.state.registers.set(key_idx, key)
        self.instruction.append_argument(StackValue(key_idx))
        self.instruction.return_value = StackValue(return_idx)

        inst_sload(self.instruction, self.state)
        actual_register = self.state.registers.get(return_idx)
        actual_storage = self.state.storage.get(key)

        self.assertEqual(expected, actual_register)
        self.assertEqual(expected, actual_storage)

    ################ SSTORE #####################
    def test_store_concrete_key_concrete_value(self):
        key = 0
        value = 0xcafebabe
        expected = 0xcafebabe

        self.create_instruction(self.SSTORE_INST)
        self.instruction.append_argument(ConcreteStackValue(key))
        self.instruction.append_argument(ConcreteStackValue(value))

        inst_sstore(self.instruction, self.state)
        actual = self.state.storage.get(key)

        self.assertEqual(expected, actual)

    def test_store_concrete_key_symbolic_value(self):
        key = 0
        value = BitVec('2', WORD_SIZE)
        value_idx = 1
        expected = BitVec('2', WORD_SIZE)

        self.create_instruction(self.SSTORE_INST)
        self.instruction.append_argument(ConcreteStackValue(key))
        self.state.registers.set(value_idx, value)
        self.instruction.append_argument(StackValue(value_idx))

        inst_sstore(self.instruction, self.state)
        actual = self.state.storage.get(key)

        self.assertEqual(expected, actual)

    def test_store_symbolic_key_concrete_value(self):
        key = BitVec('3', WORD_SIZE)
        key_idx = 0
        value = 0xcafebabe
        expected = 0xcafebabe

        self.create_instruction(self.SSTORE_INST)
        self.state.registers.set(key_idx, key)
        self.instruction.append_argument(StackValue(key_idx))
        self.instruction.append_argument(ConcreteStackValue(value))

        inst_sstore(self.instruction, self.state)
        actual = self.state.storage.get(key)

        self.assertEqual(expected, actual)

    def test_store_symbolic_key_symbolic_value(self):
        key = BitVec('3', WORD_SIZE)
        key_idx = 0
        value = BitVec('4', WORD_SIZE)
        value_idx = 1
        expected = BitVec('4', WORD_SIZE)

        self.create_instruction(self.SSTORE_INST)
        self.state.registers.set(key_idx, key)
        self.instruction.append_argument(StackValue(key_idx))
        self.state.registers.set(value_idx, value)
        self.instruction.append_argument(StackValue(value_idx))

        inst_sstore(self.instruction, self.state)
        actual = self.state.storage.get(key)

        self.assertEqual(expected, actual)

    ################ JUMP #####################
    def test_jump(self):
        destination = 0xca
        func = SSAFunction(0, 'test')
        parent_block = SSABasicBlock(0, func)
        self.instruction = SSAInstruction(EVMAsm.assemble_one(self.JUMP_INST), parent_block)
        self.instruction.append_argument(ConcreteStackValue(destination))
        dest_block = SSABasicBlock(0xca, func)
        parent_block.jump_edges.add(dest_block)
        expected = [(dest_block, None)]

        actual = inst_jump(self.instruction, self.state)

        self.assertEqual(expected, actual)

    def test_jump_with_falltrough_block(self):
        destination = 0xca
        func = SSAFunction(0, 'test')
        parent_block = SSABasicBlock(0, func)
        self.instruction = SSAInstruction(EVMAsm.assemble_one(self.JUMP_INST), parent_block)
        self.instruction.append_argument(ConcreteStackValue(destination))
        dest_block = SSABasicBlock(0xca, func)
        parent_block.fallthrough_edge = dest_block
        expected = [(dest_block, None)]

        actual = inst_jump(self.instruction, self.state)

        self.assertEqual(expected, actual)

    ################ JUMPI #####################
    def test_jumpi_true_condition(self):
        destination = 0xca
        condition = 1
        func = SSAFunction(0, 'test')
        parent_block = SSABasicBlock(0, func)
        self.instruction = SSAInstruction(EVMAsm.assemble_one(self.JUMPI_INST), parent_block)
        self.instruction.append_argument(ConcreteStackValue(destination))
        self.instruction.append_argument(ConcreteStackValue(condition))
        dest_block = SSABasicBlock(0xca, func)
        parent_block.jump_edges.add(dest_block)
        expected = [(dest_block, None)]

        actual = inst_jumpi(self.instruction, self.state)

        self.assertEqual(expected, actual)

    def test_jumpi_false_condition(self):
        destination = 0xca
        condition = 0
        func = SSAFunction(0, 'test')
        parent_block = SSABasicBlock(0, func)
        self.instruction = SSAInstruction(EVMAsm.assemble_one(self.JUMPI_INST), parent_block)
        self.instruction.append_argument(ConcreteStackValue(destination))
        self.instruction.append_argument(ConcreteStackValue(condition))
        dest_block = SSABasicBlock(0xca, func)
        parent_block.fallthrough_edge = dest_block
        expected = [(dest_block, None)]

        actual = inst_jumpi(self.instruction, self.state)

        self.assertEqual(expected, actual)

    def test_jumpi_symbolic_condition(self):
        destination = 0xca
        condition = If(BitVec('x', WORD_SIZE) < 3, BitVecVal(1, WORD_SIZE), BitVecVal(0, WORD_SIZE))
        condition_idx = 1
        func = SSAFunction(0, 'test')
        parent_block = SSABasicBlock(0, func)
        self.instruction = SSAInstruction(EVMAsm.assemble_one(self.JUMPI_INST), parent_block)
        self.instruction.append_argument(ConcreteStackValue(destination))
        self.state.registers.set(condition_idx, condition)
        self.instruction.append_argument(StackValue(condition_idx))
        true_block = SSABasicBlock(0xca, func)
        false_block = SSABasicBlock(0xac, func)
        parent_block.jump_edges.add(true_block)
        parent_block.fallthrough_edge = false_block
        expected = [(false_block, condition == 0), (true_block, condition != 0)]

        actual = inst_jumpi(self.instruction, self.state)

        self.assertEqual(expected, actual)

    ################ PC #####################
    def test_pc(self):
        return_idx = 0
        expected = 0xcaf

        self.create_instruction(self.PC_INST)
        self.instruction.return_value = StackValue(return_idx)
        self.instruction.offset = 0xcaf

        inst_pc(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ MSIZE #####################
    def test_msize(self):
        return_idx = 0
        expected = 32
        mem = self.state.memory
        mem.extend(0, 32)

        self.create_instruction(self.MSIZE_INST)
        self.instruction.return_value = StackValue(return_idx)

        inst_msize(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ GAS #####################
    def test_gas(self):
        return_idx = 0
        expected = BitVec('0', WORD_SIZE)

        self.create_instruction(self.GAS_INST)
        self.instruction.return_value = StackValue(return_idx)

        inst_gas(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ JUMPDEST #####################
    def test_jumpdest(self):
        self.create_instruction(self.JUMPDEST_INST)

        self.assertRaises(Exception, inst_jumpdest, self.instruction, self.state)
