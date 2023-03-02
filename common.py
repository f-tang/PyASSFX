
def set_font_scale(x: int, y: int):
    return "\\fscx%d\\fscy%d" % (x, y)


def set_alignment(pos: int):
    position =  min(max(1, pos), 9)
    return "\\an%d" % position


def set_position(x: float, y: float):
    return "\\pos(%.3f,%.3f)" % (x, y)


def set_movement(x1: float, y1: float, x2: float, y2: float,
                 t1: int, t2: int):
    return "\\move(%.3f,%.3f,%.3f,%.3f,%d,%d)" % (x1, y1, x2, y2, t1, t2)


def set_simple_fade(t1: int, t2: int):
    return "\\fad(t1, t2)"


def set_fade(a1: int, a2: int, a3: int,
             t1: int, t2: int, t3: int, t4: int):
    return "\\fade(%d,%d,%d,%d,%d,%d,%d)" % (a1, a2, a3, t1, t2, t3, t4)



