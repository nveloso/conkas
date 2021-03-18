import unittest

from z3 import *

from sym_exec.memory import Memory


class TestMemory(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.memory = Memory()

    def tearDown(self):
        pass

    def test_memory_all_concrete_values(self):
        self.memory.extend(0, 32)
        self.memory.store(0, 0xdeadbeef, 32)
        actual = self.memory.load(0, 32)
        expected = 0xdeadbeef

        self.assertEqual(expected, actual)

    def test_memory_all_symbolic_values(self):
        self.memory.extend(0, 32)
        self.memory.store(0, BitVec('x', 256), 32)
        actual = self.memory.load(0, 32)
        expected = BitVec('x', 256)

        self.assertEqual(expected, actual)

    def test_memory_concrete_value_first(self):
        self.memory.extend(0, 2)
        self.memory.store(0, 0xbeef, 2)
        self.memory.extend(2, 32)
        sym = BitVec('x', 256)
        self.memory.store(2, sym, 32)
        actual = self.memory.load(0, 32)
        expected = simplify(Concat(BitVecVal(0xbeef, 16), *[Extract(i, i - 7, sym) for i in range(255, 15, -8)]))

        self.assertEqual(expected, actual)

    def test_memory_symbolic_value_first(self):
        self.memory.extend(0, 3)
        self.memory.store(0, BitVec('x', 24), 3)
        self.memory.store(3, 0xbeef, 2)
        self.memory.store(5, BitVec('y', 216), 27)
        actual = self.memory.load(0, 32)
        expected = simplify(Concat(BitVec('x', 24), BitVecVal(0xbeef, 16), BitVec('y', 216)))

        self.assertEqual(expected, actual)

    def test_memory_empty_in_the_middle(self):
        self.memory.extend(0, 2)
        self.memory.store(0, 0xbeef, 2)
        self.memory.store(5, BitVec('x', 40), 5)
        actual = self.memory.load(0, 40)
        expected = simplify(Concat(BitVecVal(0xbeef, 16), BitVecVal(0, 24), BitVec('x', 40), BitVecVal(0, 176)))

        actual_mem_size = self.memory.size
        expected_mem_size = 32

        self.assertEqual(expected, actual)
        self.assertEqual(expected_mem_size, actual_mem_size)

    def test_memory_symbolic_index(self):
        sym_idx = BitVec('x', 8)
        self.memory.store(sym_idx, 0xbeef, 2)
        actual = self.memory.load(sym_idx, 2)
        expected = 0xbeef

        self.assertEqual(expected, actual)
