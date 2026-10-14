import math
import sys

sys.stdout.reconfigure(encoding='utf-8')

def render_math_curve(expr_str: str, width: int = 65, height: int = 34, x_min: float = -4.0, x_max: float = 4.0) -> tuple[int, int, list[list[tuple[int, int, int]]]]:
    safe_ns = {
        'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
        'asin': math.asin, 'acos': math.acos, 'atan': math.atan,
        'sinh': math.sinh, 'cosh': math.cosh, 'tanh': math.tanh,
        'exp': math.exp, 'log': math.log, 'ln': math.log, 'log10': math.log10,
        'sqrt': math.sqrt, 'pi': math.pi, 'e': math.e, 'abs': abs, 'pow': pow
    }
    
    clean = expr_str.replace('^', '**')
    
    def f(x_val):
        try:
            ns = dict(safe_ns)
            ns['x'] = x_val
            val = eval(clean, {'__builtins__': {}}, ns)
            if isinstance(val, (int, float)) and not math.isnan(val) and not math.isinf(val):
                return float(val)
        except Exception:
            pass
        return None

    xs = [x_min + (x_max - x_min) * (i / (width - 1)) for i in range(width)]
    ys = [f(x) for x in xs]
    valid_ys = [y for y in ys if y is not None and abs(y) < 1000]
    
    if not valid_ys:
        y_min, y_max = -5.0, 5.0
    else:
        y_min, y_max = min(valid_ys), max(valid_ys)
        if y_max - y_min < 1e-4:
            y_max += 1.0
            y_min -= 1.0
        padding = (y_max - y_min) * 0.15
        y_min -= padding
        y_max += padding

    # Pixel buffer: height x width of RGB tuples
    pixels = [[(18, 22, 28) for _ in range(width)] for _ in range(height)]
    
    # Draw Grid
    for py in range(0, height, 6):
        for px in range(width):
            pixels[py][px] = (35, 42, 54)
    for px in range(0, width, 10):
        for py in range(height):
            pixels[py][px] = (35, 42, 54)

    # Origin py
    if y_min <= 0 <= y_max:
        y0_py = int((y_max - 0) / (y_max - y_min) * (height - 1))
        y0_py = max(0, min(height - 1, y0_py))
        for px in range(width):
            pixels[y0_py][px] = (100, 125, 150)
    else:
        y0_py = height - 1 if y_max < 0 else 0

    # Origin px
    if x_min <= 0 <= x_max:
        x0_px = int((0 - x_min) / (x_max - x_min) * (width - 1))
        x0_px = max(0, min(width - 1, x0_px))
        for py in range(height):
            pixels[py][x0_px] = (100, 125, 150)
    else:
        x0_px = 0

    # Shaded Area under curve between x=-1 and x=2
    int_a, int_b = -1.0, 2.0
    for px in range(width):
        x = x_min + (x_max - x_min) * (px / (width - 1))
        if int_a <= x <= int_b:
            y = f(x)
            if y is not None:
                py_curve = int((y_max - y) / (y_max - y_min) * (height - 1))
                py_curve = max(0, min(height - 1, py_curve))
                start_y = min(y0_py, py_curve)
                end_y = max(y0_py, py_curve)
                for py in range(start_y, end_y + 1):
                    r, g, b = pixels[py][px]
                    pixels[py][px] = (int(r*0.35 + 0*0.65), int(g*0.35 + 130*0.65), int(b*0.35 + 200*0.65))

    # Curve points
    curve_points = []
    for px in range(width):
        x = x_min + (x_max - x_min) * (px / (width - 1))
        y = f(x)
        if y is not None and not math.isnan(y) and not math.isinf(y):
            py = int((y_max - y) / (y_max - y_min) * (height - 1))
            if 0 <= py < height:
                curve_points.append((px, py))
            else:
                curve_points.append(None)
        else:
            curve_points.append(None)

    # Line rasterization
    for i in range(len(curve_points) - 1):
        pt1 = curve_points[i]
        pt2 = curve_points[i+1]
        if pt1 is not None and pt2 is not None:
            x1, y1 = pt1
            x2, y2 = pt2
            steps = max(abs(x2 - x1), abs(y2 - y1), 1)
            for s in range(steps + 1):
                cur_x = int(round(x1 + (x2 - x1) * (s / steps)))
                cur_y = int(round(y1 + (y2 - y1) * (s / steps)))
                if 0 <= cur_x < width and 0 <= cur_y < height:
                    pixels[cur_y][cur_x] = (0, 240, 210) # Bright Cyan

    # Origin marker (gold dot)
    if 0 <= x0_px < width and 0 <= y0_py < height:
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if 0 <= y0_py + dy < height and 0 <= x0_px + dx < width:
                    pixels[y0_py + dy][x0_px + dx] = (255, 215, 0)

    return width, height, pixels

def pixels_to_terminal(w, h, pixels, title="Function Curve"):
    lines = []
    lines.append("┌" + "─" * (w + 2) + "┐")
    t = (title[:w-2] + "..") if len(title) > w else title
    lines.append(f"│ {t:<{w}} │")
    lines.append("├" + "─" * (w + 2) + "┤")
    for y in range(0, h, 2):
        row_top = pixels[y]
        row_bot = pixels[y + 1] if y + 1 < h else None
        line = ["│ "]
        for x in range(w):
            rt, gt, bt = row_top[x]
            if row_bot:
                rb, gb, bb = row_bot[x]
                line.append(f"\033[38;2;{rt};{gt};{bt};48;2;{rb};{gb};{bb}m▀\033[0m")
            else:
                line.append(f"\033[38;2;{rt};{gt};{bt}m▀\033[0m")
        line.append(" │")
        lines.append("".join(line))
    lines.append("└" + "─" * (w + 2) + "┘")
    return "\n".join(lines)

w, h, pxs = render_math_curve("(x**3 + 1)/(x + 1)", width=65, height=34)
print(pixels_to_terminal(w, h, pxs, "Replica: f(x) = (x^3+1)/(x+1)"))
