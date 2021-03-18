class Environment:
    def __init__(self, contract_code=None):
        self._contract_code = contract_code

    @property
    def contract_code(self):
        return self._contract_code
