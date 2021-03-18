import unittest

from rattle import EVMAsm, SSABasicBlock, SSAFunction, StackValue
from sym_exec.instructions.blockchain_context import *
from sym_exec.state import State
from sym_exec.utils import *


class TestBlockchainContext(unittest.TestCase):
    BLOCKHASH_INST = 'BLOCKHASH'
    COINBASE_INST = 'COINBASE'
    TIMESTAMP_INST = 'TIMESTAMP'
    NUMBER_INST = 'NUMBER'
    DIFFICULTY_INST = 'DIFFICULTY'
    GASLIMIT_INST = 'GASLIMIT'

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

    ################ BLOCKHASH #####################
    def test_blockhash(self):
        blockNumber = 5
        return_idx = 0
        expected = BitVec('block_number_5', WORD_SIZE)
        self.create_instruction(self.BLOCKHASH_INST)

        self.instruction.append_argument(ConcreteStackValue(blockNumber))
        self.instruction.return_value = StackValue(return_idx)

        inst_blockhash(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ COINBASE #####################
    def test_coinbase(self):
        return_idx = 0
        expected = BitVec('coinbase', WORD_SIZE)
        self.create_instruction(self.COINBASE_INST)

        self.instruction.return_value = StackValue(return_idx)

        inst_coinbase(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ TIMESTAMP #####################
    def test_timestamp(self):
        return_idx = 0
        expected = BitVec('timestamp', WORD_SIZE)
        self.create_instruction(self.TIMESTAMP_INST)

        self.instruction.return_value = StackValue(return_idx)

        inst_timestamp(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ NUMBER #####################
    def test_number(self):
        return_idx = 0
        expected = BitVec('number', WORD_SIZE)
        self.create_instruction(self.NUMBER_INST)

        self.instruction.return_value = StackValue(return_idx)

        inst_number(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ DIFFICULTY #####################
    def test_difficulty(self):
        return_idx = 0
        expected = BitVec('difficulty', WORD_SIZE)
        self.create_instruction(self.DIFFICULTY_INST)

        self.instruction.return_value = StackValue(return_idx)

        inst_difficulty(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    ################ GASLIMIT #####################
    def test_gaslimit(self):
        return_idx = 0
        expected = BitVec('gaslimit', WORD_SIZE)
        self.create_instruction(self.GASLIMIT_INST)

        self.instruction.return_value = StackValue(return_idx)

        inst_gaslimit(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)
