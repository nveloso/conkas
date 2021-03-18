import unittest

from rattle import EVMAsm, SSABasicBlock, SSAFunction, StackValue
from sym_exec.instructions.crypto import *
from sym_exec.state import State
from sym_exec.utils import *


class TestCrypto(unittest.TestCase):
    SHA3_INST = 'SHA3'

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

    ################ SHA3 #####################
    def test_sha3_concrete_values(self):
        offset = 28
        length = 4
        return_idx = 0
        expected = 0xd4fd4e189132273036449fc9e11198c739161b4c0116a9a2dccdfa1c492006f1

        mem = self.state.memory
        mem.extend(0, 4)
        mem.store(0, 0xdeadbeef)

        self.create_instruction(self.SHA3_INST)
        self.instruction.append_argument(ConcreteStackValue(offset))
        self.instruction.append_argument(ConcreteStackValue(length))
        self.instruction.return_value = StackValue(return_idx)

        inst_sha3(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_sha3_with_length_zero(self):
        offset = 12
        length = 0
        return_idx = 0
        expected = 0xc5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470

        mem = self.state.memory
        mem.extend(0, 32)
        mem.store(0, 0xdeadbeef)

        self.create_instruction(self.SHA3_INST)
        self.instruction.append_argument(ConcreteStackValue(offset))
        self.instruction.append_argument(ConcreteStackValue(length))
        self.instruction.return_value = StackValue(return_idx)

        inst_sha3(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_sha3_more_than_a_word(self):
        offset = 7
        length = 41
        return_idx = 0
        expected = 0x4b019278dda180155f30f40b06574f99ed517e2f7af7d7d2636e49b7a04dde7a

        mem = self.state.memory
        mem.extend(0, 32)
        mem.store(0, 0xdeadbeef)
        mem.extend(32, 32)
        mem.store(32, 0xcafebabe)

        self.create_instruction(self.SHA3_INST)
        self.instruction.append_argument(ConcreteStackValue(offset))
        self.instruction.append_argument(ConcreteStackValue(length))
        self.instruction.return_value = StackValue(return_idx)

        inst_sha3(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_sha3_memory_not_extended(self):
        offset = 7
        length = 57
        return_idx = 0
        expected = 0x5b1a666ab9caf701291104c2e5b7cc9089bdbe46ff78a3f7b165e06f893ea879

        mem = self.state.memory
        mem.extend(0, 32)
        mem.store(0, 0xdeadbeef)

        self.create_instruction(self.SHA3_INST)
        self.instruction.append_argument(ConcreteStackValue(offset))
        self.instruction.append_argument(ConcreteStackValue(length))
        self.instruction.return_value = StackValue(return_idx)

        inst_sha3(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_sha3_length_symbolic(self):
        offset = 7
        length = BitVec('%2', WORD_SIZE)
        length_idx = 1
        return_idx = 0
        expected = BitVec('0', WORD_SIZE)

        mem = self.state.memory
        mem.extend(0, 32)
        mem.store(0, 0xdeadbeef)

        self.create_instruction(self.SHA3_INST)
        self.instruction.append_argument(ConcreteStackValue(offset))
        self.state.registers.set(length_idx, length)
        self.instruction.append_argument(StackValue(length_idx))
        self.instruction.return_value = StackValue(return_idx)

        inst_sha3(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_sha3_offset_symbolic(self):
        offset = BitVec('%2', WORD_SIZE)
        offset_idx = 1
        length = 52
        return_idx = 0
        expected = BitVec('0', WORD_SIZE)

        mem = self.state.memory
        mem.extend(0, 32)
        mem.store(0, 0xdeadbeef)

        self.create_instruction(self.SHA3_INST)
        self.state.registers.set(offset_idx, offset)
        self.instruction.append_argument(StackValue(offset_idx))
        self.instruction.append_argument(ConcreteStackValue(length))
        self.instruction.return_value = StackValue(return_idx)

        inst_sha3(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)
