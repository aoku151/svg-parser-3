import sys
import os
from svgelements import SVG, Rect

MARGIN = 5

# -----------------------------
# すべての子要素を再帰的に取得
# -----------------------------
def iter_all_elements(svg):
    for e in svg:
        yield e
        if hasattr(e, "__iter__"):
            for child in iter_all_elements(e):
                yield child

# -----------------------------
# SVG 1ファイル処理
# -----------------------------
def process_svg(input_path, output_path, fill_color="#ffffff"):
    svg = SVG.parse(input_path)

    min_x = float("inf")
    min_y = float("inf")
    max_x = float("-inf")
    max_y = float("-inf")

    found = False

    for e in iter_all_elements(svg):
        try:
            bbox = e.bbox()
        except Exception:
            continue

        if bbox is None:
            continue

        # Rect または tuple の両対応
        if isinstance(bbox, tuple):
            x, y, w, h = bbox
        else:
            x, y, w, h = bbox.x, bbox.y, bbox.width, bbox.height

        found = True
        min_x = min(min_x, x)
        min_y = min(min_y, y)
        max_x = max(max_x, x + w)
        max_y = max(max_y, y + h)

    if not found:
        print(f"Skip (no shapes): {input_path}")
        return

    inner_x = min_x + MARGIN
    inner_y = min_y + MARGIN
    inner_width = (max_x - min_x) - 2 * MARGIN
    inner_height = (max_y - min_y) - 2 * MARGIN

    rect = Rect(
        x=inner_x,
        y=inner_y,
        width=inner_width,
        height=inner_height,
    )
    rect.stroke = fill_color
    rect.stroke_width = 5
    rect.fill = fill_color

    svg.append(rect)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg.tostring())

    print(f"Processed: {input_path} → {output_path}")

# -----------------------------
# メイン処理（ディレクトリ一括）
# -----------------------------
if __name__ == "__main__":
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    os.makedirs(output_dir, exist_ok=True)

    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith(".svg"):
                inp = os.path.join(root, file)
                out = os.path.join(output_dir, file)
                process_svg(inp, out)
