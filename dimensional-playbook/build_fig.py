#!/usr/bin/env python3
"""立體化敘事使用手冊的示範圖：一個等角實體方塊，標出「視覺深度」的三個要素。

規格檔紀律（KB-19 第三層）：真尺寸只在規格來源區誕生，畫圖區只准引用。
用法：
    python3 build_fig.py > demo.svg
"""
import math

# @figure-spec-source
# 這張是示範圖，不是量測圖：方塊的尺寸是為了讓三個面都看得清楚而選的。
CUBE_SIZE_MM = 150.0                                    # 示範方塊的邊長
CUBE_ORIGIN_X_MM = 0.0                                  # 方塊原點
CUBE_ORIGIN_Y_MM = 0.0
CUBE_ORIGIN_Z_MM = 0.0
ISO_ANGLE_DEG = 30.0                                    # 等角投影角
TOP_LIGHTNESS = 1.00                                    # 頂面：最亮（光從上來）
LEFT_LIGHTNESS = 0.72                                   # 左側面：中間
RIGHT_LIGHTNESS = 0.48                                  # 右側面：最暗
VIEWBOX_PAD_MM = 62.0                                   # viewBox 四周留白
BADGE_R_MM = 21.0                                       # 引線圓標半徑
BADGE_SIZE_MM = 27                                      # 圓標字級
BADGE_TEXT_BASELINE_RATIO = 0.35                        # 圓標字基線相對字級的位移
LEAD_LEN_MM = 74.0                                      # 引線長度
DOT_R_MM = 4.5                                          # 引線端點實心圓半徑
STROKE_MM = 1.6                                         # 線寬
QUAD_VERTS = 4                                          # 一個面有幾個頂點
LEAD_VERT_RATIO = 0.62                                  # 引線縱向長度相對橫向的比例
# @end-figure-spec-source


# @figure-spec
def iso(x, y, z):
    c = math.cos(math.radians(ISO_ANGLE_DEG))
    s = math.sin(math.radians(ISO_ANGLE_DEG))
    return ((x - y) * c, (x + y) * s - z)


def path_of(pts):
    return "M" + " L".join("%.1f %.1f" % p for p in pts) + " Z"


def centroid(pts):
    return (sum(p[0] for p in pts) / float(QUAD_VERTS),
            sum(p[1] for p in pts) / float(QUAD_VERTS))


def build():
    o = (CUBE_ORIGIN_X_MM, CUBE_ORIGIN_Y_MM, CUBE_ORIGIN_Z_MM)
    s = CUBE_SIZE_MM

    def v(dx, dy, dz):
        return iso(o[0] + dx * s, o[1] + dy * s, o[2] + dz * s)

    top = [v(0, 0, 1), v(1, 0, 1), v(1, 1, 1), v(0, 1, 1)]
    left = [v(0, 1, 1), v(1, 1, 1), v(1, 1, 0), v(0, 1, 0)]
    right = [v(1, 0, 1), v(1, 1, 1), v(1, 1, 0), v(1, 0, 0)]

    parts = []
    for face, light in ((top, TOP_LIGHTNESS), (left, LEFT_LIGHTNESS), (right, RIGHT_LIGHTNESS)):
        parts.append('<path d="%s" fill="var(--solid)" fill-opacity="%.2f" '
                     'stroke="var(--plate-bg)" stroke-width="%.1f"/>'
                     % (path_of(face), light, STROKE_MM))

    allpts = top + left + right
    anchors = [("A", centroid(top), -1, -1),
               ("B", centroid(left), -1, 1),
               ("C", centroid(right), 1, 1)]
    for letter, (ax, ay), sx, sy in anchors:
        bx = ax + sx * LEAD_LEN_MM
        by = ay + sy * LEAD_LEN_MM * LEAD_VERT_RATIO
        parts.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="var(--plate-fg)"/>'
                     % (ax, ay, DOT_R_MM))
        parts.append('<path d="M%.1f %.1f L%.1f %.1f" fill="none" stroke="var(--plate-fg)" '
                     'stroke-width="%.1f"/>' % (ax, ay, bx, by, STROKE_MM))
        parts.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="var(--plate-fg)"/>'
                     % (bx, by, BADGE_R_MM))
        parts.append('<text x="%.1f" y="%.1f" font-size="%d" font-weight="700" '
                     'text-anchor="middle" fill="var(--plate-bg)">%s</text>'
                     % (bx, by + BADGE_SIZE_MM * BADGE_TEXT_BASELINE_RATIO,
                        BADGE_SIZE_MM, letter))
        allpts.append((bx + BADGE_R_MM * sx, by + BADGE_R_MM * sy))

    xs = [p[0] for p in allpts]
    ys = [p[1] for p in allpts]
    minx, maxx = min(xs) - VIEWBOX_PAD_MM, max(xs) + VIEWBOX_PAD_MM
    miny, maxy = min(ys) - VIEWBOX_PAD_MM, max(ys) + VIEWBOX_PAD_MM
    bg = ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="var(--plate-bg)"/>'
          % (minx, miny, maxx - minx, maxy - miny))
    return ('<svg viewBox="%.1f %.1f %.1f %.1f" role="img" aria-labelledby="dt dd">'
            '<title id="dt">視覺深度的三個要素：頂面、兩個側面、以及它們之間的明暗差</title>'
            '<desc id="dd">一個以等角投影畫出的方塊，三個面同時可見。'
            '頂面最亮、左側面次之、右側面最暗，三者用同一個顏色的不同透明度做出來。'
            '圓標 A 指頂面，B 指左側面，C 指右側面。'
            '這個方塊沒有任何座標軸與刻度——深度只讓它看起來有實體，不供讀出數值。</desc>'
            '%s%s</svg>'
            % (minx, miny, maxx - minx, maxy - miny, bg, "".join(parts)))
# @end-figure-spec


if __name__ == "__main__":
    print(build())
