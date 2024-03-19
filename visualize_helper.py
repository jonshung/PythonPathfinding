def lerp_color(x, col1: list, col2: list):
    f0 = (col2[0] - col1[0])
    f1 = (col2[1] - col1[1])
    f2 = (col2[2] - col1[2])
    if(len(col1) < 3):
        col1[3] = 255
    if(len(col2) < 3):
        col2[3] = 255
    f3 = col2[3] - col1[3]
    return [round(x * f0 + col1[0]), round(x * f1 + col1[1]), round(x * f2 + col1[2]), round(x * f3 + col1[3])]

def ramp_vl(x, max_x, ramps) -> int:
    return round((x / max_x) * ramps)