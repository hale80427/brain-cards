#!/usr/bin/env python3
"""第 252 跑 R3：把 blog-to-bill 的圖 1 換成 SVG 等角實體（KB-19 第四層手法 ①）。

彥皓 2026-09-06 V0：三種立體手法裡選 ①（有厚度、三個面、明暗，資訊仍是 2D）。

規格檔紀律（KB-19 第三層）：真尺寸只在規格來源區誕生，畫圖區只准引用。
用法：
    python3 build_figs.py > fig1.svg
"""
import math

# @figure-spec-source
# 訊號管道沿傳播方向的四個轉換點；管寬是「傳播規模」的示意值，不是量測值。
STATION_X_MM = [0.0, 95.0, 190.0, 285.0, 380.0]        # 四段的分界站位
NARR_HALFSIZE_MM = [12.0, 24.0, 38.0, 54.0, 72.0]      # 擬人化語彙：逐段擴張
ENG_HALFSIZE_MM = 12.0                                  # 工程語彙：全程等寬
ENG_SOLID_END_MM = 190.0                                # 工程語彙實體段的終點
ENG_FADE_END_MM = 262.0                                 # 虛線段的終點（第二天被駁倒）
ENG_LIFT_MM = 176.0                                     # 工程語彙管抬高多少（z 方向）
ISO_ANGLE_DEG = 30.0                                    # 等角投影角
START_BLOCK_X0_MM = -62.0                               # 共同起點方塊的左端
START_BLOCK_X1_MM = -8.0                                # 共同起點方塊的右端
START_BLOCK_HALFSIZE_MM = 16.0                          # 共同起點方塊的半邊長
START_BLOCK_LIFT_MM = 88.0                              # 起點方塊抬高多少
VIEWBOX_PAD_MM = 40.0                                   # viewBox 四周留白
RAMP_BREAK_LO = 0.25                                    # 色帶：青轉琥珀的斷點
RAMP_BREAK_HI = 0.75                                    # 色帶：琥珀轉紅的斷點
QUAD_VERTS = 4                                          # 一個面有幾個頂點
SEG_LABEL_BASELINE_MM = 11                              # 段號基線相對重心的位移
SEG_LABEL_SIZE_MM = 32                                  # 段號字級
BADGE_R_MM = 23.0                                       # A／B／C 圓標半徑
BADGE_SIZE_MM = 30                                      # A／B／C 字級
BADGE_LEAD_MM = 34.0                                    # 圓標與被指位置之間的引線長
SIDE_OPACITY = 0.62                                     # 側面相對頂面的明暗比
LINK_WIDTH_MM = 3.0                                     # 起點方塊到兩條管的連接線粗細
BADGE_TEXT_BASELINE_RATIO = 0.35                        # 圓標字的基線相對字級的位移
BADGE_ANCHOR_RATIO = 0.4                                # 引線終點相對引線長的比例
BADGE_B_LIFT_RATIO = 0.5                                # B 圓標相對半徑的上移比例
BADGE_B_ANCHOR_RATIO = 0.3                              # B 引線終點的縱向比例
BADGE_C_OUT_RATIO = 1.1                                 # C 圓標往外推的比例
BADGE_C_LIFT_RATIO = 0.6                                # C 圓標相對半徑的下移比例
BADGE_BBOX_RATIO_TOP = 2.0                              # A 圓標納入 bbox 時多留幾個半徑
BADGE_BBOX_RATIO_BOT = 1.8                              # C 圓標納入 bbox 時多留幾個半徑
# @end-figure-spec-source

SEGMENTS = len(STATION_X_MM) - 1


# @figure-spec
def iso(x, y, z):
    """等角投影。x 沿傳播方向，y 是管寬，z 是高度。"""
    c = math.cos(math.radians(ISO_ANGLE_DEG))
    s = math.sin(math.radians(ISO_ANGLE_DEG))
    return ((x - y) * c, (x + y) * s - z)


def box_faces(x0, x1, s0, s1, lift):
    """一段管子的兩個可見面：頂面與近側面。"""
    top = [iso(x0, -s0, s0 + lift), iso(x1, -s1, s1 + lift),
           iso(x1, s1, s1 + lift), iso(x0, s0, s0 + lift)]
    side = [iso(x0, s0, s0 + lift), iso(x1, s1, s1 + lift),
            iso(x1, s1, -s1 + lift), iso(x0, s0, -s0 + lift)]
    return top, side


def path_of(pts):
    return "M" + " L".join("%.1f %.1f" % p for p in pts) + " Z"


def centroid(pts):
    return (sum(p[0] for p in pts) / float(QUAD_VERTS),
            sum(p[1] for p in pts) / float(QUAD_VERTS))


def ramp(t):
    if t < RAMP_BREAK_LO:
        return "var(--plate-teal)"
    if t < RAMP_BREAK_HI:
        return "var(--plate-amber)"
    return "var(--plate-red)"


def badge(cx, cy, ax, ay, letter, parts):
    """圓標＋引線。圓標放在 (cx,cy)，引線指向 (ax,ay)。"""
    parts.append('<path d="M%.1f %.1f L%.1f %.1f" fill="none" '
                 'stroke="var(--plate-dim)" stroke-width="2"/>' % (cx, cy, ax, ay))
    parts.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="var(--plate-fg)"/>'
                 % (cx, cy, BADGE_R_MM))
    parts.append('<text x="%.1f" y="%.1f" font-size="%d" font-weight="700" '
                 'text-anchor="middle" fill="var(--plate-bg)">%s</text>'
                 % (cx, cy + BADGE_SIZE_MM * BADGE_TEXT_BASELINE_RATIO, BADGE_SIZE_MM, letter))


def build():
    parts = []
    allpts = []

    # 擬人化語彙：四段逐段擴張的實體管
    for i in range(SEGMENTS):
        x0, x1 = STATION_X_MM[i], STATION_X_MM[i + 1]
        s0, s1 = NARR_HALFSIZE_MM[i], NARR_HALFSIZE_MM[i + 1]
        top, side = box_faces(x0, x1, s0, s1, 0.0)
        allpts += top + side
        parts.append('<path d="%s" fill="url(#gtop%d)" stroke="var(--plate-bg)" '
                     'stroke-width="1.3"/>' % (path_of(top), i))
        parts.append('<path d="%s" fill="url(#gside%d)" stroke="var(--plate-bg)" '
                     'stroke-width="1.3"/>' % (path_of(side), i))
        cx, cy = centroid(top)
        parts.append('<text x="%.1f" y="%.1f" font-size="%d" font-weight="700" '
                     'text-anchor="middle" fill="var(--plate-bg)">%d</text>'
                     % (cx, cy + SEG_LABEL_BASELINE_MM, SEG_LABEL_SIZE_MM, i + 1))
    funnel_end = box_faces(STATION_X_MM[-2], STATION_X_MM[-1],
                           NARR_HALFSIZE_MM[-2], NARR_HALFSIZE_MM[-1], 0.0)[1]

    # 工程語彙：等寬管（實體段）
    top, side = box_faces(0.0, ENG_SOLID_END_MM, ENG_HALFSIZE_MM, ENG_HALFSIZE_MM, ENG_LIFT_MM)
    allpts += top + side
    parts.append('<path d="%s" fill="var(--plate-teal)" stroke="var(--plate-bg)" '
                 'stroke-width="1.3"/>' % path_of(top))
    parts.append('<path d="%s" fill="var(--plate-teal)" fill-opacity="%.2f" '
                 'stroke="var(--plate-bg)" stroke-width="1.3"/>'
                 % (path_of(side), SIDE_OPACITY))
    # 工程語彙：虛線段（第二天被駁倒之後）
    top2, side2 = box_faces(ENG_SOLID_END_MM, ENG_FADE_END_MM,
                            ENG_HALFSIZE_MM, ENG_HALFSIZE_MM, ENG_LIFT_MM)
    allpts += top2 + side2
    parts.append('<path d="%s" fill="none" stroke="var(--plate-teal)" stroke-width="2" '
                 'stroke-dasharray="8 7"/>' % path_of(top2))
    parts.append('<path d="%s" fill="none" stroke="var(--plate-teal)" stroke-width="2" '
                 'stroke-dasharray="8 7" stroke-opacity="%.2f"/>'
                 % (path_of(side2), SIDE_OPACITY))

    # 共同起點方塊
    st_top, st_side = box_faces(START_BLOCK_X0_MM, START_BLOCK_X1_MM,
                                START_BLOCK_HALFSIZE_MM, START_BLOCK_HALFSIZE_MM,
                                START_BLOCK_LIFT_MM)
    allpts += st_top + st_side
    parts.append('<path d="%s" fill="var(--plate-line)" stroke="var(--plate-bg)" '
                 'stroke-width="1.3"/>' % path_of(st_top))
    parts.append('<path d="%s" fill="var(--plate-line)" fill-opacity="%.2f" '
                 'stroke="var(--plate-bg)" stroke-width="1.3"/>'
                 % (path_of(st_side), SIDE_OPACITY))

    # 起點方塊到兩條管的連接線：讓「同一個起點分兩條」在形狀上看得到
    link_from = iso(START_BLOCK_X1_MM, 0.0, START_BLOCK_LIFT_MM)
    link_eng = iso(0.0, 0.0, ENG_LIFT_MM)
    link_narr = iso(0.0, 0.0, NARR_HALFSIZE_MM[0])
    parts.insert(0, '<path d="M%.1f %.1f L%.1f %.1f" fill="none" stroke="var(--plate-teal)" '
                    'stroke-width="%.1f" stroke-linecap="round"/>'
                    % (link_from[0], link_from[1], link_eng[0], link_eng[1], LINK_WIDTH_MM))
    parts.insert(1, '<path d="M%.1f %.1f L%.1f %.1f" fill="none" stroke="var(--plate-amber)" '
                    'stroke-width="%.1f" stroke-linecap="round"/>'
                    % (link_from[0], link_from[1], link_narr[0], link_narr[1], LINK_WIDTH_MM))

    # 三個圓標：A 指起點方塊、B 指工程語彙終止處、C 指喇叭末端
    ax, ay = centroid(st_top)
    badge(ax, ay - BADGE_LEAD_MM - BADGE_R_MM, ax,
          ay - BADGE_LEAD_MM * BADGE_ANCHOR_RATIO, "A", parts)
    bx, by = centroid(top2)
    badge(bx + BADGE_LEAD_MM, by - BADGE_LEAD_MM - BADGE_R_MM * BADGE_B_LIFT_RATIO,
          bx + BADGE_LEAD_MM * BADGE_ANCHOR_RATIO,
          by - BADGE_LEAD_MM * BADGE_B_ANCHOR_RATIO, "B", parts)
    cx, cy = centroid(funnel_end)
    badge(cx + BADGE_LEAD_MM * BADGE_C_OUT_RATIO,
          cy + BADGE_LEAD_MM + BADGE_R_MM * BADGE_C_LIFT_RATIO,
          cx + BADGE_LEAD_MM * BADGE_ANCHOR_RATIO,
          cy + BADGE_LEAD_MM * BADGE_ANCHOR_RATIO, "C", parts)
    allpts += [(ax, ay - BADGE_LEAD_MM - BADGE_R_MM * BADGE_BBOX_RATIO_TOP),
               (cx + BADGE_LEAD_MM * BADGE_C_OUT_RATIO,
                cy + BADGE_LEAD_MM + BADGE_R_MM * BADGE_BBOX_RATIO_BOT)]

    xs = [p[0] for p in allpts]
    ys = [p[1] for p in allpts]
    minx, maxx = min(xs) - VIEWBOX_PAD_MM, max(xs) + VIEWBOX_PAD_MM
    miny, maxy = min(ys) - VIEWBOX_PAD_MM, max(ys) + VIEWBOX_PAD_MM

    defs = ['<defs>']
    for i in range(SEGMENTS):
        t0 = i / float(SEGMENTS)
        t1 = (i + 1) / float(SEGMENTS)
        defs.append('<linearGradient id="gtop%d" x1="0" y1="0" x2="1" y2="0">'
                    '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/>'
                    '</linearGradient>' % (i, ramp(t0), ramp(t1)))
        defs.append('<linearGradient id="gside%d" x1="0" y1="0" x2="1" y2="0">'
                    '<stop offset="0" stop-color="%s" stop-opacity="%.2f"/>'
                    '<stop offset="1" stop-color="%s" stop-opacity="%.2f"/>'
                    '</linearGradient>' % (i, ramp(t0), SIDE_OPACITY, ramp(t1), SIDE_OPACITY))
    defs.append('</defs>')

    bg = ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="var(--plate-bg)"/>'
          % (minx, miny, maxx - minx, maxy - miny))
    return ('<svg viewBox="%.1f %.1f %.1f %.1f" role="img" aria-labelledby="f1t f1d">'
            '<title id="f1t">兩種措辭造成的兩條傳播路徑，畫成有厚度的立體管道</title>'
            '<desc id="f1d">兩條從同一個立體方塊出發的管道，以等角投影畫出頂面與側面。'
            '上方那條全程等寬，中途改為虛線後終止；下方那條沿四個編號段逐段變粗，'
            '顏色由青轉紅。圓標 A 指共同起點，B 指上方那條的終止處，C 指下方那條的末端。</desc>'
            '%s%s%s</svg>'
            % (minx, miny, maxx - minx, maxy - miny, "".join(defs), bg, "".join(parts)))
# @end-figure-spec


if __name__ == "__main__":
    print(build())
