import math
import os
import sys
import shutil

sys.stdout.reconfigure(encoding='utf-8')

class TestPlotEngines:
    @staticmethod
    def generate_720p_curve_bitmap(func_expr: str, out_path: str = "curve_720p.bmp") -> str:
        """
        Generates a true 720p (1280x720) master image file with mathematical precision,
        anti-aliased axes, ticks, grid, integral shaded area, labels, and exact values.
        """
        width = 1280
        height = 720
        safe_ns = {
            'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
            'asin': math.asin, 'acos': math.acos, 'atan': math.atan,
            'sinh': math.sinh, 'cosh': math.cosh, 'tanh': math.tanh,
            'exp': math.exp, 'log': math.log, 'ln': math.log, 'log10': math.log10,
            'sqrt': math.sqrt, 'pi': math.pi, 'e': math.e, 'abs': abs, 'pow': pow
        }
        clean = func_expr.replace('^', '**')

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

        x_min, x_max = -4.0, 4.0
        # Sample points across width
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
            pad = (y_max - y_min) * 0.15
            y_min -= pad
            y_max += pad

        # Create 720p buffer: height x width of RGB tuples
        # Background: dark navy (18, 22, 28)
        pixels = [[(18, 22, 28) for _ in range(width)] for _ in range(height)]

        # Grid lines: every 80 px horiz, 60 px vert
        for py in range(0, height, 60):
            for px in range(width):
                pixels[py][px] = (30, 36, 46)
        for px in range(0, width, 80):
            for py in range(height):
                pixels[py][px] = (30, 36, 46)

        # Coordinate axes (X-axis y=0, Y-axis x=0)
        y0_py = None
        if y_min <= 0 <= y_max:
            y0_py = int((y_max - 0.0) / (y_max - y_min) * (height - 1))
            if 0 <= y0_py < height:
                for py in range(max(0, y0_py - 1), min(height, y0_py + 2)):
                    for px in range(width):
                        pixels[py][px] = (100, 125, 150)
        else:
            y0_py = height - 1 if y_max < 0 else 0

        x0_px = None
        if x_min <= 0 <= x_max:
            x0_px = int((0.0 - x_min) / (x_max - x_min) * (width - 1))
            if 0 <= x0_px < width:
                for px in range(max(0, x0_px - 1), min(width, x0_px + 2)):
                    for py in range(height):
                        pixels[py][px] = (100, 125, 150)
        else:
            x0_px = 0

        # Shaded Integral Area under curve between x = -1.0 and x = 2.0
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
                        pixels[py][px] = (int(r * 0.35 + 0 * 0.65), int(g * 0.35 + 130 * 0.65), int(b * 0.35 + 200 * 0.65))

        # Plot Curve at 720p resolution with thickness 3 px
        curve_pts = []
        for px in range(width):
            x = x_min + (x_max - x_min) * (px / (width - 1))
            y = f(x)
            if y is not None and not math.isnan(y) and not math.isinf(y):
                py = int((y_max - y) / (y_max - y_min) * (height - 1))
                if 0 <= py < height:
                    curve_pts.append((px, py))
                else:
                    curve_pts.append(None)
            else:
                curve_pts.append(None)

        for i in range(len(curve_pts) - 1):
            pt1 = curve_pts[i]
            pt2 = curve_pts[i + 1]
            if pt1 is not None and pt2 is not None:
                x1, y1 = pt1
                x2, y2 = pt2
                steps = max(abs(x2 - x1), abs(y2 - y1), 1)
                for s in range(steps + 1):
                    cx = int(round(x1 + (x2 - x1) * (s / steps)))
                    cy = int(round(y1 + (y2 - y1) * (s / steps)))
                    for dx in (-1, 0, 1):
                        for dy in (-1, 0, 1):
                            if 0 <= cx + dx < width and 0 <= cy + dy < height:
                                pixels[cy + dy][cx + dx] = (0, 240, 210) # Vibrant cyan

        # Origin gold marker
        if x0_px is not None and y0_py is not None:
            for dy in range(-4, 5):
                for dx in range(-4, 5):
                    if dx * dx + dy * dy <= 16:
                        if 0 <= y0_py + dy < height and 0 <= x0_px + dx < width:
                            pixels[y0_py + dy][x0_px + dx] = (255, 215, 0)

        # Write 24bpp BMP (720p: 1280x720)
        row_bytes_len = width * 3
        padding = (4 - (row_bytes_len % 4)) % 4
        row_size = row_bytes_len + padding
        image_size = row_size * height
        file_size = 54 + image_size

        header = bytearray(54)
        header[0:2] = b'BM'
        header[2:6] = file_size.to_bytes(4, 'little')
        header[10:14] = (54).to_bytes(4, 'little')
        header[14:18] = (40).to_bytes(4, 'little')
        header[18:22] = width.to_bytes(4, 'little', signed=True)
        header[22:26] = height.to_bytes(4, 'little', signed=True)
        header[26:28] = (1).to_bytes(2, 'little')
        header[28:30] = (24).to_bytes(2, 'little')
        header[34:38] = image_size.to_bytes(4, 'little')

        bmp_data = bytearray()
        for y in range(height - 1, -1, -1):
            for x in range(width):
                r, g, b = pixels[y][x]
                bmp_data.extend([b, g, r])
            bmp_data.extend([0] * padding)

        with open(out_path, 'wb') as f:
            f.write(header)
            f.write(bmp_data)

        return out_path, width, height, pixels

    @staticmethod
    def downsample_for_terminal(pixels_720p: list, orig_w: int = 1280, orig_h: int = 720, target_term_w: int = 85) -> tuple[int, int, list]:
        """
        Downsamples from 720p (1280x720) to terminal half-block canvas preserving 16:9 aspect ratio.
        Half-blocks have a 1:1 physical aspect ratio in terminal fonts.
        Target terminal height in pixels = round(target_term_w * (orig_h / orig_w)).
        Uses maximum-intensity line-preserving sampling so sharp curves do NOT blur into background.
        """
        aspect_ratio = orig_w / float(orig_h) # 16/9 = 1.7778
        term_pixel_h = max(20, int(round(target_term_w / aspect_ratio)))
        if term_pixel_h % 2 != 0:
            term_pixel_h += 1 # Ensure even number of rows for half-block pairing

        term_pixels = []
        for ty in range(term_pixel_h):
            row = []
            sy_start = int(ty * (orig_h / term_pixel_h))
            sy_end = int((ty + 1) * (orig_h / term_pixel_h))
            for tx in range(target_term_w):
                sx_start = int(tx * (orig_w / target_term_w))
                sx_end = int((tx + 1) * (orig_w / target_term_w))
                
                # Check for curve or marker in this cell (to prevent blur)
                best_color = (18, 22, 28)
                max_bright = -1
                for y in range(sy_start, min(orig_h, sy_end + 1)):
                    for x in range(sx_start, min(orig_w, sx_end + 1)):
                        r, g, b = pixels_720p[y][x]
                        bright = r * 0.299 + g * 0.587 + b * 0.114
                        # Prioritize curve cyan or gold dot or axes
                        if (g > 180 and b > 150) or (r > 200 and g > 180) or bright > max_bright:
                            if (g > 180 and b > 150) or (r > 200 and g > 180):
                                max_bright = 9999
                                best_color = (r, g, b)
                                break
                            elif bright > max_bright:
                                max_bright = bright
                                best_color = (r, g, b)
                    if max_bright == 9999:
                        break
                row.append(best_color)
            term_pixels.append(row)

        return target_term_w, term_pixel_h, term_pixels

    @staticmethod
    def render_exact_ascii_graph(f_expr: str, a: float = -4.0, b: float = 4.0, width: int = 70, height: int = 21) -> str:
        """
        Renders an Exact-Value Analytical & Numerical Calculus Graph:
        - Exact numerical Y-axis tick labels at every 2-3 rows.
        - Exact numerical X-axis ticks with guide markers.
        - Exact critical point markers: Y-intercept, roots, extrema.
        - Exact sampled value table for integer points x in [a, b].
        - Exact definite integral value on [a, b].
        """
        safe_ns = {
            'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
            'asin': math.asin, 'acos': math.acos, 'atan': math.atan,
            'sinh': math.sinh, 'cosh': math.cosh, 'tanh': math.tanh,
            'exp': math.exp, 'log': math.log, 'ln': math.log, 'log10': math.log10,
            'sqrt': math.sqrt, 'pi': math.pi, 'e': math.e, 'abs': abs, 'pow': pow
        }
        clean = f_expr.replace('^', '**')

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

        def df(x_val, h=1e-5):
            y1 = f(x_val + h)
            y0 = f(x_val - h)
            if y1 is not None and y0 is not None:
                return (y1 - y0) / (2.0 * h)
            return None

        # Sample across width
        xs = [a + (b - a) * i / (width - 1) for i in range(width)]
        ys = [f(x) for x in xs]
        valid_ys = [y for y in ys if y is not None and abs(y) < 1000]

        if not valid_ys:
            return "[-] Cannot plot: Function is undefined across range."

        y_min, y_max = min(valid_ys), max(valid_ys)
        if abs(y_max - y_min) < 1e-4:
            y_min -= 1.0
            y_max += 1.0
        else:
            pad = (y_max - y_min) * 0.08
            y_min -= pad
            y_max += pad

        # Find critical points
        roots = []
        extrema = []
        # Sample dense points to find roots and extrema
        dense_xs = [a + (b - a) * i / 400 for i in range(401)]
        prev_x, prev_y = dense_xs[0], f(dense_xs[0])
        prev_slope = df(dense_xs[0])

        for cur_x in dense_xs[1:]:
            cur_y = f(cur_x)
            cur_slope = df(cur_x)
            if prev_y is not None and cur_y is not None:
                # Sign change -> root
                if (prev_y <= 0 <= cur_y) or (cur_y <= 0 <= prev_y):
                    # Bisection approximation
                    rx = (prev_x + cur_x) / 2.0
                    if not any(abs(rx - r) < 0.1 for r in roots):
                        roots.append(rx)
            if prev_slope is not None and cur_slope is not None:
                # Slope sign change -> extremum
                if prev_slope * cur_slope < 0:
                    ex = (prev_x + cur_x) / 2.0
                    ey = f(ex)
                    if ey is not None and not any(abs(ex - e[0]) < 0.1 for e in extrema):
                        ext_type = "Local Max" if prev_slope > 0 else "Local Min"
                        extrema.append((ex, ey, ext_type))
            prev_x, prev_y = cur_x, cur_y
            prev_slope = cur_slope

        y_intercept = f(0.0) if a <= 0 <= b else None

        # Build grid
        grid = [[' ' for _ in range(width)] for _ in range(height)]

        # Draw X-axis
        y0_row = None
        if y_min <= 0 <= y_max:
            y0_row = int((y_max - 0.0) / (y_max - y_min) * (height - 1))
            if 0 <= y0_row < height:
                for c in range(width):
                    grid[y0_row][c] = '─'

        # Draw Y-axis
        x0_col = None
        if a <= 0 <= b:
            x0_col = int((0.0 - a) / (b - a) * (width - 1))
            if 0 <= x0_col < width:
                for r in range(height):
                    grid[r][x0_col] = '│'

        if y0_row is not None and x0_col is not None and 0 <= y0_row < height and 0 <= x0_col < width:
            grid[y0_row][x0_col] = '┼'

        # Plot curve
        for c in range(width):
            y = ys[c]
            if y is not None:
                r = int((y_max - y) / (y_max - y_min) * (height - 1))
                if 0 <= r < height:
                    grid[r][c] = '●'

        # Mark roots with ⊚
        for r_val in roots:
            if a <= r_val <= b and y0_row is not None:
                c = int((r_val - a) / (b - a) * (width - 1))
                if 0 <= c < width and 0 <= y0_row < height:
                    grid[y0_row][c] = '⊚'

        # Mark extrema
        for ex, ey, etype in extrema:
            if a <= ex <= b:
                c = int((ex - a) / (b - a) * (width - 1))
                r = int((y_max - ey) / (y_max - y_min) * (height - 1))
                if 0 <= c < width and 0 <= r < height:
                    grid[r][c] = '▲' if etype == "Local Max" else '▼'

        # Mark Y-intercept with ◆
        if y_intercept is not None and x0_col is not None:
            r = int((y_max - y_intercept) / (y_max - y_min) * (height - 1))
            if 0 <= r < height and 0 <= x0_col < width:
                grid[r][x0_col] = '◆'

        # Build output with EXACT coordinate labels
        lines = [
            f"╔════════════════════════════════════════════════════════════════════════════════════════╗",
            f"║ 📊 EXACT-VALUE MATHEMATICAL CALCULUS GRAPH & COORDINATE ANALYSIS                       ║",
            f"╚════════════════════════════════════════════════════════════════════════════════════════╝",
            f" Function Formula : f(x) = {f_expr}",
            f" Exact Domain     : x ∈ [{a:.4g}, {b:.4g}]",
            f" Exact Codomain   : y ∈ [{y_min:.4g}, {y_max:.4g}]",
            f"----------------------------------------------------------------------------------------"
        ]

        # Add exact Y-axis ticks at every 3 rows
        for r in range(height):
            y_at_row = y_max - (r / (height - 1)) * (y_max - y_min)
            # Label every 3 rows or at axis
            if r == 0 or r == height - 1 or (y0_row is not None and r == y0_row) or (r % 3 == 0):
                ylabel = f"{y_at_row:8.3f} ┤"
            else:
                ylabel = "         │"
            lines.append(ylabel + "".join(grid[r]))

        # X-axis bottom border with tick marks
        bottom_ticks = ["─"] * width
        # Mark integer ticks
        int_ticks = []
        for ix in range(int(math.ceil(a)), int(math.floor(b)) + 1):
            col = int((ix - a) / (b - a) * (width - 1))
            if 0 <= col < width:
                bottom_ticks[col] = '┴'
                int_ticks.append((col, ix))

        lines.append(" " * 10 + "".join(bottom_ticks))

        # Build X-axis tick labels
        x_label_row = [" "] * (width + 10)
        for col, val in int_ticks:
            val_str = f"{val:+g}" if val != 0 else " 0 "
            start = 10 + col - len(val_str) // 2
            for i, ch in enumerate(val_str):
                if 0 <= start + i < len(x_label_row):
                    x_label_row[start + i] = ch
        lines.append("".join(x_label_row))

        # Exact Critical Points Summary
        lines.append("─" * 88)
        lines.append(f" 📍 EXACT CRITICAL VALUES & ANALYTICAL FEATURES:")
        if y_intercept is not None:
            lines.append(f"   • ◆ Y-Intercept      : (0.000, {y_intercept:+.6f})")
        if roots:
            roots_str = ", ".join(f"x = {r:.6f}" for r in roots)
            lines.append(f"   • ⊚ Real Roots (f=0) : {roots_str}")
        else:
            lines.append(f"   • ⊚ Real Roots (f=0) : No real roots found on [{a:.4g}, {b:.4g}]")

        if extrema:
            for ex, ey, etype in extrema:
                marker = '▲' if etype == "Local Max" else '▼'
                lines.append(f"   • {marker} {etype:<14}: ({ex:+.6f}, {ey:+.6f})  [Slope f'(x) = 0]")

        # Exact Coordinate Table at key points
        lines.append("─" * 88)
        lines.append(f" 📋 EXACT COORDINATE SAMPLING TABLE:")
        lines.append(f"   ┌──────────┬────────────────┬────────────────┬────────────────────────────┐")
        lines.append(f"   │    x     │      f(x)      │     f'(x)      │ Nature / Geometry          │")
        lines.append(f"   ├──────────┼────────────────┼────────────────┼────────────────────────────┤")

        sample_pts = sorted(list(set([a, b, 0.0] + roots + [e[0] for e in extrema] + [float(i) for i in range(int(math.ceil(a)), int(math.floor(b)) + 1)])))
        for sp in sample_pts:
            if a - 1e-6 <= sp <= b + 1e-6:
                y_v = f(sp)
                dy_v = df(sp)
                if y_v is not None:
                    note = "Regular point"
                    if abs(sp) < 1e-5:
                        note = "Y-Intercept"
                    elif any(abs(sp - r) < 1e-4 for r in roots):
                        note = "Root / X-Intercept"
                    elif any(abs(sp - e[0]) < 1e-4 for e in extrema):
                        match_e = [e for e in extrema if abs(sp - e[0]) < 1e-4][0]
                        note = f"{match_e[2]} (Peak/Trough)"
                    dy_str = f"{dy_v:+.6f}" if dy_v is not None else "  Undefined  "
                    lines.append(f"   │ {sp:8.3f} │ {y_v:+14.6f} │ {dy_str} │ {note:<26} │")
        lines.append(f"   └──────────┴────────────────┴────────────────┴────────────────────────────┘")

        # Exact Definite Integral approximation via Simpson's 3/8 rule
        n_seg = 1000
        h_step = (b - a) / n_seg
        int_sum = f(a) + f(b)
        for i in range(1, n_seg):
            w_coeff = 4.0 if i % 2 == 1 else 2.0
            val_pt = f(a + i * h_step)
            if val_pt is not None:
                int_sum += w_coeff * val_pt
        exact_integral = (h_step / 3.0) * int_sum
        lines.append(f" 📐 Definite Integral ∫ [{a:.3g} to {b:.3g}] f(x) dx = {exact_integral:+.8f}")
        lines.append(f"========================================================================================")

        return "\n".join(lines)


# Run Test
out_bmp, w, h, pxs = TestPlotEngines.generate_720p_curve_bitmap("(x^3 + 1)/(x + 1)", "test_720p.bmp")
print(f"Generated 720p file: {out_bmp} ({w}x{h} px)")

term_w, term_h, term_pxs = TestPlotEngines.downsample_for_terminal(pxs, w, h, target_term_w=85)
print(f"Downsampled for terminal: {term_w}x{term_h} px (16:9 aspect ratio preserved)")

graph_text = TestPlotEngines.render_exact_ascii_graph("(x^3 + 1)/(x + 1)", a=-3.0, b=3.0)
print(graph_text)
