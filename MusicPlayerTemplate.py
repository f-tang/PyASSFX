import os
from argparse import ArgumentParser
from common import *

import pyonfx

PREV_LINE_NUM = 2
NEXT_LINE_NUM = 3
MOVEMENT_TIME_MS = 300
LINE_DISTANCE_RATE = 1.
FADE_TIME = 300
MAIN_LINE_SCALE = 100
SUB_LINE_SCALE = 70
PREV_LINE_OPACITY = 128


def make_cur_line(line: pyonfx.Line, line_style: str = "MainStyle", is_moving: bool = True):
    line_dist = int(line.height * LINE_DISTANCE_RATE)
    new_line = line.copy()
    new_line.style = line_style
    if len(new_line.actor) > 0:
        new_line.style += "-%s" % new_line.actor
    movement_time = min(MOVEMENT_TIME_MS, new_line.duration)
    an = set_alignment(5)
    movement = set_movement(line.center, line.middle + line_dist,
                            line.center, line.middle,
                            0, movement_time)
    position = set_position(line.center, line.middle)
    scale = set_font_scale(MAIN_LINE_SCALE, MAIN_LINE_SCALE) if line_style == "MainStyle" \
        else set_font_scale(SUB_LINE_SCALE, SUB_LINE_SCALE)
    new_line.text = (
            "{%s%s%s}%s"
            % (an, scale, movement if is_moving else position,
               line.text
               )
    )
    return new_line


def make_prev_line(current_line: pyonfx.Line, prev_line: pyonfx.Line,
                   idx: int, line_style: str = "SubStyle", is_moving: bool = True):
    line_dist = int(current_line.height * LINE_DISTANCE_RATE)
    new_line = current_line.copy()
    new_line.layer = idx
    new_line.style = line_style
    new_line.actor = prev_line.actor
    if len(new_line.actor) > 0:
        new_line.style += "-%s" % new_line.actor
    new_line.y = current_line.y - line_dist * idx
    movement_time = min(MOVEMENT_TIME_MS, new_line.duration)
    fade_time = min(FADE_TIME, new_line.duration)
    an = set_alignment(5)
    movement = set_movement(
                    current_line.center, current_line.middle - line_dist * (idx - 1),
                    current_line.center, current_line.middle - line_dist * idx,
                    0, movement_time,
                )
    position = set_position(current_line.center, current_line.middle - line_dist * idx)
    font_scale = set_font_scale(MAIN_LINE_SCALE, MAIN_LINE_SCALE) if line_style == "MainStyle" \
        else set_font_scale(SUB_LINE_SCALE, SUB_LINE_SCALE)
    opacity = int(PREV_LINE_OPACITY + (255 - PREV_LINE_OPACITY) / max(1, PREV_LINE_NUM) * max(0, idx - 1))
    if 0 < idx < PREV_LINE_NUM:
        fade = set_fade(0, opacity, opacity, 0, fade_time, fade_time, fade_time)
        new_line.text = (
                "{\\%s%s%s%s}%s"
                % (an, font_scale, movement if is_moving else position, fade,
                   prev_line.text
                   )
        )
    elif idx == PREV_LINE_NUM:
        fade = set_fade(opacity, opacity, 255,
                        0, fade_time, max(new_line.duration - fade_time, fade_time), new_line.duration)
        new_line.text = (
                "{\\%s%s%s%s}%s"
                % (an, font_scale, movement if is_moving else position, fade,
                   prev_line.text
                   )
        )
    return new_line


def make_next_line(current_line: pyonfx.Line, next_line: pyonfx.Line,
                   idx: int, line_style: str = "SubStyle", is_moving: bool = True):
    line_dist = int(current_line.height * LINE_DISTANCE_RATE)
    new_line = current_line.copy()
    new_line.layer = idx + PREV_LINE_NUM
    new_line.style = line_style
    new_line.actor = next_line.actor
    if len(new_line.actor) > 0:
        new_line.style += "-%s" % new_line.actor
    new_line.y = current_line.y + line_dist * idx
    movement_time = min(MOVEMENT_TIME_MS, new_line.duration)
    fade_time = min(FADE_TIME, new_line.duration)
    an = set_alignment(5)
    movement = set_movement(
        current_line.center, current_line.middle + line_dist * (idx + 1),
        current_line.center, current_line.middle + line_dist * idx,
        0, movement_time
    )
    position = set_position(current_line.center, current_line.middle + line_dist * idx)
    scale = set_font_scale(MAIN_LINE_SCALE, MAIN_LINE_SCALE) if line_style == "MainStyle" \
        else set_font_scale(SUB_LINE_SCALE, SUB_LINE_SCALE)
    if 0 < idx < NEXT_LINE_NUM:
        new_line.text = (
                "{\\%s%s%s}%s"
                % (an, scale, movement if is_moving else position,
                   next_line.text
                   )
        )
    elif idx == NEXT_LINE_NUM:
        simple_fade = set_simple_fade(fade_time, 0)
        new_line.text = (
                "{\\%s%s%s%s}%s"
                % (an, scale, movement if is_moving else position, simple_fade,
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
                io_ass.write_line(make_prev_line(lines[i], lines[i - j], j, is_moving=True))

        motion = not (i == 0)
        io_ass.write_line(make_cur_line(lines[i], is_moving=motion))

        for j in range(1, NEXT_LINE_NUM + 1):
            next_style = "MainStyle" if (i + j) == (len(lines) - 1) else "SubStyle"
            if (i + j) < len(lines):
                io_ass.write_line(make_next_line(lines[i], lines[i + j], j, next_style, motion))

    io_ass.save()
