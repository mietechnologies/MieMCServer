"""
A simple module for working with files.
"""

from util.logger import log

def add(lines: list, to_file_at_path: str) -> bool:
    """
    """

    existing = lines_from_file(to_file_at_path)

    new_lines = []
    for _, line in enumerate(lines):
        if "\n" not in line and line not in existing:
            new_lines.append(f'{line}\n')
        else:
            new_lines.append(line)

    with open(to_file_at_path, 'w', encoding='utf8') as file_out:
        for line in new_lines:
            file_out.write(line)

def update(file_at_path: str, replacing_line: str, with_line: str) -> bool:
    """
    """

    lines = lines_from_file(file_at_path)
    with open(file_at_path, 'w', encoding='utf8') as file_out:
        for line in lines:
            if line == replacing_line:
                file_out.write(with_line)
            else:
                file_out.write(line)
    return True

def lines_from_file(file: str, delete_fetched: bool = False):
    """
    """

    lines = []
    with open(file, 'r', encoding='utf8') as file_in:
        temp_lines = file_in.readlines()
        with open(file, 'w', encoding='utf8') as file_out:
            for line in temp_lines:
                # Always preserve all comments and empty lines when fetching commands from a file:
                if '#' in line:
                    file_out.write(line)
                elif line == '\n':
                    file_out.write(line)
                # If line is command and fetched commands should be kept:
                elif not delete_fetched:
                    lines.append(line.replace('\n', ''))
                    file_out.write(line)
                # If line is command and fetched commands should be removed:
                elif delete_fetched:
                    lines.append(line.replace('\n', ''))
                # Otherwise, the line is unhandled; log the line that was encountered and keep
                # it in the file
                else:
                    log('Line from {} not recognized [{}]'.format(file, line))
                    file_out.write(line)
    return lines
