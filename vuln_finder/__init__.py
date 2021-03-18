from vuln_finder.arithmetic import arithmetic_analyse
from vuln_finder.reentrancy import reentrancy_analyse
from vuln_finder.time_manipulation import time_manipulation_analyse
from vuln_finder.transaction_ordering_dependence import tod_analyse
from vuln_finder.unchecked_ll_calls import unchecked_low_level_calls_analyse

available_modules = {
    'arithmetic': arithmetic_analyse,
    'reentrancy': reentrancy_analyse,
    'time_manipulation': time_manipulation_analyse,
    'transaction_ordering_dependence': tod_analyse,
    'unchecked_ll_calls': unchecked_low_level_calls_analyse
}
