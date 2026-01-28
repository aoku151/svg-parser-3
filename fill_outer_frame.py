import sys
import os
from svgpathtools import svg2paths2
from lxml import etree

MARGIN = 5

def process_svg(input_path, output_path, fill_color="#ffffff"):
    # svgpathtools でパスと属性を取得
    paths, attributes, svg_attr = svg2paths2(input_path)

    min_x = float("inf")
    min_y = float("inf")
    max_x = float("-inf")
    max_y = float("-inf")

    found = False

    # すべての path の bbox を取得
    for p in paths:
        xmin, xmax, ymin, ymax = p.bbox()

        found = True
        min_x = min(min_x, xmin)
        min_y = min(min_y, ymin)
        max_x = max(max_x, xmax)
        max_y = max(max_y, ymax)

    if not found:
        print(f"Skip (no shapes): {input_path}")
        return

    # rect の位置とサイズ
    inner_x = min_x + MARGIN
    inner_y = min_y + MARGIN
    inner_width = (max_x - min_x) - 2 * MARGIN
    inner_height = (max_y - min_y) - 2 * MARGIN

    # lxml で元 SVG を読み込む
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(input_path, parser)
    root = tree.getroot()

    # rect 要素を作成
    rect = etree.Element("rect")
    rect.set("x", str(inner_x))
    rect.set("y", str(inner_y))
    rect.set("width", str(inner_width))
    rect.set("height", str(inner_height))
    rect.set("stroke", fill_color)
    rect.set("stroke-width", "5")
    rect.set("fill", fill_color)

    # rect を root の末尾に追加（svg-parser-2 と同じ）
    root.append(rect)

    # 保存（整形して書き出し）
    tree.write(
        output_path,
        pretty_print=True,
        xml_declaration=True,
        encoding="utf-8"
    )

    print(f"Processed: {input_path} → {output_path}")


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
