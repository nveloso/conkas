from sym_exec.analyzed_block import AnalyzedBlock


class Vulnerability(object):
    def __init__(self, vuln_type: str, analyzed_block: AnalyzedBlock, pc, instruction_offset, model=None):
        if model is None:
            model = {}
        self._type = vuln_type
        self._analyzed_block = analyzed_block
        self._function_name = analyzed_block.block.function.name
        self._pc = pc
        self._instruction_offset = instruction_offset
        self._model = model
        self._line_number = None

    @property
    def type(self):
        return self._type

    @property
    def analyzed_block(self):
        return self._analyzed_block

    @property
    def function_name(self):
        return self._function_name

    @function_name.setter
    def function_name(self, function_name):
        assert (isinstance(function_name, str))

        self._function_name = function_name

    @property
    def pc(self):
        return self._pc

    @property
    def instruction_offset(self):
        return self._instruction_offset

    @property
    def model(self):
        return self._model

    @property
    def line_number(self):
        return self._line_number

    @line_number.setter
    def line_number(self, value):
        assert isinstance(value, int)
        self._line_number = value

    def __repr__(self):
        return f"Vulnerability('{self._type}', {self._analyzed_block}, {self._pc}, {self._instruction_offset})"

    def __hash__(self):
        return hash(
            (self._type, self._line_number if self._line_number is not None else self._instruction_offset))

    def __eq__(self, other):
        if not isinstance(other, Vulnerability):
            raise NotImplementedError
        return self._type == other._type and \
               self._line_number == other._line_number if self._line_number is not None else self._instruction_offset == other._instruction_offset
