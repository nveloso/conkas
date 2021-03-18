import json
import logging
from subprocess import PIPE, Popen

logger = logging.getLogger(__name__)


class SourceMap:
    def __init__(self, filename, solc_path='solc'):
        self._filename = filename
        self._solc_path = solc_path
        self._mapping = {}
        self._create_mapping()

    def _get_source_map_runtime(self):
        cmd = [self._solc_path, '--combined-json', 'srcmap-runtime', self._filename]
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)

        stdout, stderr = p.communicate()
        ret = p.returncode

        if ret != 0:
            logger.error('Cannot get source map runtime. Check if solc is in your path environment variable')
            raise Exception
        out = stdout.decode('UTF-8')
        return json.loads(out)

    @staticmethod
    def _find_lower_bound(target, array):
        start = 0
        length = len(array)
        while length > 0:
            half = length >> 1
            middle = start + half
            if array[middle] <= target:
                length = length - 1 - half
                start = middle + 1
            else:
                length = half
        return start - 1

    @staticmethod
    def _convert_from_char_position(pos, line_break_positions):
        line = SourceMap._find_lower_bound(pos, line_break_positions)
        if line_break_positions[line] != pos:
            line = line + 1
        return line

    @staticmethod
    def _convert_offset_to_line(start, line_break_positions):
        if start >= 0:
            return SourceMap._convert_from_char_position(start, line_break_positions)

    def _get_solc_mappings(self, srcmap, contract, all_line_breaks):
        """The line mappings function"""
        prev_item = []
        pc = 0
        for item in srcmap:
            mapping = item.split(":")
            mapping += prev_item[len(mapping):]  # if the length is less than previous mapping length then take the previous mapping values of the rest
            for index in range(len(mapping)):
                if mapping[index] == "":  # Fill up all empty values with it's previous values
                    mapping[index] = int(prev_item[index])

            offset, length, idx, _ = mapping  # offset:length:file_no:jump format
            idx = int(idx)
            if idx == -1:
                prev_item = mapping
                pc += 1
                continue

            offset = int(offset)
            line_break_positions = all_line_breaks[idx]
            lineno = SourceMap._convert_offset_to_line(offset, line_break_positions) + 1

            prev_item = mapping
            self._mapping[(contract, pc)] = lineno
            pc += 1

    def _create_mapping(self):
        sourcemap_runtime = self._get_source_map_runtime()
        all_line_breaks = []
        for filename in sourcemap_runtime['sourceList']:
            with open(filename, 'rb') as file:
                code = file.read()
                i = 0
                line_breaks = []
                for ascii_number in code:
                    if ascii_number == 10: # If ascii_number is equal to 10 means equal to \n (new line)
                        line_breaks.append(i)
                    i += 1
                all_line_breaks.append(line_breaks)

        for contract in sourcemap_runtime['contracts']:
            srcmap = sourcemap_runtime['contracts'][contract]['srcmap-runtime']
            if not srcmap:
                continue
            srcmap = srcmap.split(';')
            self._get_solc_mappings(srcmap, contract, all_line_breaks)

    def get_line_number(self, contract, pc):
        return self._mapping.get((contract, pc))
