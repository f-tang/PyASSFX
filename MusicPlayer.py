import os
from argparse import ArgumentParser

import pyonfx

PREV_LINE_NUM = 2
NEXT_LINE_NUM = 3
MOVEMENT_TIME_MS = 300
LINE_DISTANCE_RATE = 1.
FADE_TIME = 300
MAIN_LINE_SCALE = 100
SUB_LINE_SCALE = 70
PREV_LINE_OPACITY = 128


def make_cur_line(line: pyonfx.Line, line_style: str = "MainStyle", motion: bool = True):
    line_dist = int(line.height * LINE_DISTANCE_RATE)
    new_line = line.copy()
    new_line.style = line_style
    movement_time = min(MOVEMENT_TIME_MS, new_line.duration)
    movement = ("\\move(%.3f,%.3f,%.3f,%.3f,%d,%d)"
                % (
                    line.center, line.middle + line_dist,
                    line.center, line.middle,
                    0, movement_time
                ))
    position = ("\\pos(%.3f,%.3f)"
                % (line.center, line.middle))
    scale = "\\fscx%d\\fscy%d" % (MAIN_LINE_SCALE, MAIN_LINE_SCALE) if line_style == "MainStyle" \
        else "\\fscx%d\\fscy%d" % (SUB_LINE_SCALE, SUB_LINE_SCALE)
    new_line.text = (
            "{\\an5%s%s}%s"
            % (
                scale,
                movement if motion else position,
                line.text
            )
    )
    return new_line


def make_prev_line(current_line: pyonfx.Line, prev_line: pyonfx.Line,
                   idx: int, line_style: str = "SubStyle", motion: bool = True):

    line_dist = int(current_line.height * LINE_DISTANCE_RATE)
    new_line = current_line.copy()
    new_line.layer = idx
    new_line.style = line_style
    new_line.actor = prev_line.actor
    new_line.y = current_line.y - line_dist * idx
    movement_time = min(MOVEMENT_TIME_MS, new_line.duration)
    fade_time = min(FADE_TIME, new_line.duration)
    movement = ("\\move(%.3f,%.3f,%.3f,%.3f,%d,%d)"
                % (
                    current_line.center, current_line.middle - line_dist * (idx - 1),
                    current_line.center, current_line.middle - line_dist * idx,
                    0, movement_time,
                ))
    position = ("\\pos(%.3f,%.3f)"
                % (current_line.center, current_line.middle - line_dist * idx))
    scale = "\\fscx%d\\fscy%d" % (MAIN_LINE_SCALE, MAIN_LINE_SCALE) if line_style == "MainStyle" \
        else "\\fscx%d\\fscy%d" % (SUB_LINE_SCALE, SUB_LINE_SCALE)
    if 0 < idx < PREV_LINE_NUM:
        fade = ("\\fade(%d,%d,%d,%d,%d,%d,%d)"
                % (0, PREV_LINE_OPACITY, PREV_LINE_OPACITY,
                   0, fade_time, fade_time, fade_time))
        new_line.text = (
                "{\\an5%s%s%s}%s"
                % (
                    scale,
                    movement if motion else position,
                    fade,
                    prev_line.text
                )
        )
    elif idx == PREV_LINE_NUM:
        fade = ("\\fade(%d,%d,%d,%d,%d,%d,%d)"
                % (PREV_LINE_OPACITY, PREV_LINE_OPACITY, 255,
                   0, fade_time, max(new_line.duration - fade_time, fade_time), new_line.duration))
        new_line.text = (
                "{\\an5%s%s%s}%s"
                % (
                    scale,
                    movement if motion else position,
                    fade,
                    prev_line.text
                )
        )

    return new_line


def make_next_line(current_line: pyonfx.Line, next_line: pyonfx.Line,
                   idx: int, line_style: str = "SubStyle", motion: bool = True):

    line_dist = int(current_line.height * LINE_DISTANCE_RATE)
    new_line = current_line.copy()
    new_line.layer = idx + PREV_LINE_NUM
    new_line.style = line_style
    new_line.actor = next_line.actor
    new_line.y = current_line.y + line_dist * idx
    movement_time = min(MOVEMENT_TIME_MS, new_line.duration)
    fade_time = min(FADE_TIME, new_line.duration)
    movement = ("\\move(%.3f,%.3f,%.3f,%.3f,%d,%d)"
                % (
                    current_line.center, current_line.middle + line_dist * (idx + 1),
                    current_line.center, current_line.middle + line_dist * idx,
                    0, movement_time,
                ))
    position = ("\\pos(%.3f,%.3f)"
                % (current_line.center, current_line.middle + line_dist * idx))
    scale = "\\fscx%d\\fscy%d" % (MAIN_LINE_SCALE, MAIN_LINE_SCALE) if line_style == "MainStyle" \
        else "\\fscx%d\\fscy%d" % (SUB_LINE_SCALE, SUB_LINE_SCALE)
    if 0 < idx < NEXT_LINE_NUM:
        new_line.text = (
                "{\\an5%s%s}%s"
                % (
                    scale,
                    movement if motion else position,
                    next_line.text
                )
        )
    elif idx == NEXT_LINE_NUM:
        new_line.text = (
                "{\\an5%s%s\\fad(%d,%d)}%s"
                % (
                    scale,
                    movement if motion else position,
                    fade_time, 0,
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
                io_ass.write_line(make_prev_line(lines[i], lines[i - j], j, motion=True))

        motion = not (i == 0)
        io_ass.write_line(make_cur_line(lines[i], motion=motion))

        for j in range(1, NEXT_LINE_NUM + 1):
            next_style = "MainStyle" if (i + j) == (len(lines) - 1) else "SubStyle"
            if (i + j) < len(lines):
                io_ass.write_line(make_next_line(lines[i], lines[i + j], j, next_style, motion))

    io_ass.save()
