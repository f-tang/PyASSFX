import os
from argparse import ArgumentParser

import pyonfx

PREV_LINE_NUM = 3
NEXT_LINE_NUM = 3
MOVEMENT_TIME_MS = 300
LINE_DISTANCE_RATE = 1.


def make_cur_line(line: pyonfx.Line):
    line_dist = int(line.height * LINE_DISTANCE_RATE)
    new_line = line.copy()
    new_line.style = "MainStyle"
    new_line.text = (
            "{\\an5\\move(%.3f,%.3f,%.3f,%.3f,%d,%d)}%s"
            % (
                line.center, line.middle + line_dist,
                line.center, line.middle,
                0, MOVEMENT_TIME_MS,
                line.text
            )
    )
    return new_line


def make_prev_line(current_line: pyonfx.Line,
                   prev_line: pyonfx.Line,
                   idx: int):
    line_dist = int(current_line.height * LINE_DISTANCE_RATE)
    new_line = current_line.copy()
    new_line.layer = idx
    new_line.style = "SubStyle"
    new_line.actor = prev_line.actor
    new_line.y = current_line.y - line_dist * idx
    if 0 < idx < PREV_LINE_NUM:
        new_line.text = (
            "{\\an5\\fscx75\\fscy75\\move(%.3f,%.3f,%.3f,%.3f,%d,%d)}%s"
        % (
                current_line.center, current_line.middle - line_dist * (idx - 1),
                current_line.center, current_line.middle - line_dist * idx,
                0, MOVEMENT_TIME_MS,
                prev_line.text
            )
        )
    elif idx == PREV_LINE_NUM:
        new_line.text = (
                "{\\an5\\fscx75\\fscy75\\move(%.3f,%.3f,%.3f,%.3f,%d,%d)}%s"
                % (
                    current_line.center, current_line.middle - line_dist * (idx - 1),
                    current_line.center, current_line.middle - line_dist * idx,
                    0, MOVEMENT_TIME_MS,
                    prev_line.text
                )
        )

    return new_line


def make_next_line(current_line: pyonfx.Line,
                   next_line: pyonfx.Line,
                   idx: int):
    line_dist = int(current_line.height * LINE_DISTANCE_RATE)
    new_line = current_line.copy()
    new_line.layer = idx + PREV_LINE_NUM
    new_line.style = "SubStyle"
    new_line.actor = next_line.actor
    new_line.y = current_line.y + line_dist * idx
    if 0 < idx < NEXT_LINE_NUM:
        new_line.text = (
                "{\\an5\\fscx75\\fscy75\\move(%.3f,%.3f,%.3f,%.3f,%d,%d)}%s"
                % (
                    current_line.center, current_line.middle + line_dist * (idx + 1),
                    current_line.center, current_line.middle + line_dist * idx,
                    0, MOVEMENT_TIME_MS,
                    next_line.text
                )
        )
    elif idx == NEXT_LINE_NUM:
        new_line.text = (
                "{\\an5\\fscx75\\fscy75\\move(%.3f,%.3f,%.3f,%.3f,%d,%d)}%s"
                % (
                    current_line.center, current_line.middle + line_dist * (idx + 1),
                    current_line.center, current_line.middle + line_dist * idx,
                    0, MOVEMENT_TIME_MS,
                    next_line.text
                )
        )

    return new_line


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--input', type=str, help="Input ASS file.")
    args = parser.parse_args()
    input_path = args.input
    if input_path is None:
        print("Please specify --input as the source ASS file")
        exit(1)

    stem, ext = os.path.splitext(input_path)
    output_path = stem + '_modified' + ext

    io_ass = pyonfx.Ass(input_path, output_path)
    meta, style, lines = io_ass.get_data()

    for i in range(len(lines)):
        for j in range(1, PREV_LINE_NUM + 1):
            if (i - j) >= 0:
                io_ass.write_line(make_prev_line(lines[i], lines[i - j], j))

        io_ass.write_line(make_cur_line(lines[i]))

        for j in range(1, NEXT_LINE_NUM + 1):
            if (i + j) < len(lines):
                io_ass.write_line(make_next_line(lines[i], lines[i + j], j))

    io_ass.save()
