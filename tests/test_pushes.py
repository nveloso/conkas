import unittest

from rattle import EVMAsm, SSABasicBlock, SSAFunction, StackValue
from sym_exec.instructions.pushes import *
from sym_exec.state import State
from sym_exec.utils import *


class TestPushes(unittest.TestCase):
    PUSH2_INST = 'PUSH2'
    PUSH5_INST = 'PUSH5'

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

    def create_instruction(self, name):
        self.instruction = SSAInstruction(EVMAsm.assemble_one(name), SSABasicBlock(0, SSAFunction(0)))

    ################ PUSH #####################
    def test_push2(self):
        value = 0xcafe
        return_idx = 0
        expected = 0xcafe

        self.create_instruction(f"{self.PUSH2_INST} {value}")
        self.instruction.append_argument(ConcreteStackValue(value))
        self.instruction.return_value = StackValue(return_idx)

        inst_push(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)

    def test_push5(self):
        value = 0xcafebabef0
        return_idx = 0
        expected = 0xcafebabef0

        self.create_instruction(f"{self.PUSH5_INST} {value}")
        self.instruction.append_argument(ConcreteStackValue(value))
        self.instruction.return_value = StackValue(return_idx)

        inst_push(self.instruction, self.state)
        actual = self.state.registers.get(return_idx)

        self.assertEqual(expected, actual)
