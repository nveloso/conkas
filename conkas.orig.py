import argparse
import logging

from solcx import get_available_solc_versions, install_solc_pragma, set_solc_version_pragma, compile_files
from solcx.exceptions import SolcNotInstalled
from solcx.install import get_executable
from solidity_parser.parser import parse

import vuln_finder.vulnerability_finder
from rattle import Recover
from solidity.source_map import SourceMap
from sym_exec import symbolic_executor
from sym_exec.symbolic_executor import SymExec
from vuln_finder import available_modules
from vuln_finder.vulnerability_finder import VulnerabilityFinder

logger = logging.getLogger()


def get_solc_version_string(file):
    parsed = parse(file.read().decode('utf-8'))
    for children in parsed['children']:
        if children['type'] == 'PragmaDirective':
            return children['value']
    return get_available_solc_versions()[0]


def get_constructor_traces(constructor_bytecode):
    ssa = Recover(constructor_bytecode, edges=[], optimize=True)

    sym_exec = SymExec(ssa)
    return sym_exec.execute()


def main():
    is_solidity_file_default = False
    log_output_default = 'Error'
    all_vuln_types = list(available_modules.keys())
    max_depth_default = 25
    find_all_vulnerabilities_default = False
    default_timeout = 100

    parser = argparse.ArgumentParser(description='Symbolic execution tool for EVM')
    parser.add_argument('file', type=argparse.FileType('rb'), help='File with EVM bytecode hex string to analyse')
    parser.add_argument('--solidity-file', '-s', action='store_true', default=is_solidity_file_default,
                        help=f'Use this option when file is a solidity file instead of EVM bytecode hex string. By default it is {"unset" if not is_solidity_file_default else "set"}')
    parser.add_argument('--verbosity', '-v', type=str, default=log_output_default,
                        help=f'Log output verbosity (NotSet, Debug, Info, Warning, Error, Critical). Default = {log_output_default}')
    parser.add_argument('--vuln-type', '-vt', action='append', default=[],
                        help=f'VULN_TYPE can be {all_vuln_types}. Default = {all_vuln_types}')
    parser.add_argument('--max-depth', '-md', type=int, default=max_depth_default,
                        help=f'Max recursion depth. The counting is how many basic blocks should be analysed. Default = {max_depth_default}')
    parser.add_argument('--find-all-vulnerabilities', '-fav', action='store_true',
                        default=find_all_vulnerabilities_default,
                        help=f'When set it will try to find all possible vulnerabilities. It will take some time. By '
                             f'default it is {"unset" if not find_all_vulnerabilities_default else "set"}')
    parser.add_argument('--timeout', '-t', type=int, default=default_timeout,
                        help=f'Timeout to Z3 Solver. Default = {default_timeout}')
    args = parser.parse_args()
    if not args.vuln_type:
        args.vuln_type = all_vuln_types

    symbolic_executor.MAX_DEPTH = args.max_depth
    vuln_finder.vulnerability_finder.Z3_TIMEOUT = args.timeout

    try:
        log_level = getattr(logging, args.verbosity.upper())
    except AttributeError:
        log_level = None

    logger.setLevel(level=log_level)
    file = args.file
    filename = file.name
    logger.info(f'Conkas running on file: {filename}')

    bytecodes = {}
    srcmap = None
    if args.solidity_file:
        solc_version = get_solc_version_string(file)
        try:
            set_solc_version_pragma(solc_version)
        except SolcNotInstalled:
            logger.info(f'Installing solc version {solc_version}...')
            install_solc_pragma(solc_version)
            set_solc_version_pragma(solc_version)
            logger.info('Installed')
        logger.info(f'Compiling {filename}...')
        contracts = compile_files([filename])
        logger.info('Compiled successfully')
        srcmap = SourceMap(filename, get_executable())
        for name, contract in contracts.items():
            runtime_bytecode = contract['bin-runtime']
            bytecodes[name] = runtime_bytecode.encode('utf-8')
    else:
        bytecodes[filename] = args.file.read()

    for name, bytecode in bytecodes.items():
        logger.info(f'Analysing {name}...')
        print(f'Analysing {name}...')
        if len(bytecode) == 0:
            logger.info('Nothing to analyse')
            print('Nothing to analyse')
            continue
        try:
            ssa = Recover(bytecode, edges=[], optimize=True)

            sym_exec = SymExec(ssa)
            traces = sym_exec.execute()

            checker = VulnerabilityFinder(traces, ssa.functions, name, srcmap, args.find_all_vulnerabilities)
            vulnerabilities_found = checker.analyse_only(args.vuln_type)
        except Exception as e:
            logger.exception(e)
            continue

        if len(vulnerabilities_found) == 0:
            continue

        for vuln in vulnerabilities_found:
            line_number = vuln.line_number
            vuln_str = f'Vulnerability: {vuln.type}. ' \
                       f'Maybe in function: {vuln.function_name}. ' \
                       f'PC: {hex(vuln.pc)}. ' \
                       f'Line number: {line_number if line_number else ""}.'
            logger.info(vuln_str)
            print(vuln_str)
            for i, (var_name, value) in enumerate(vuln.model.items()):
                if i == 0:
                    logger.info(f'If {var_name} = {value}')
                    print(f'If {var_name} = {value}')
                else:
                    logger.info(f'and {var_name} = {value}')
                    print(f'and {var_name} = {value}')


if __name__ == '__main__':
    main()
