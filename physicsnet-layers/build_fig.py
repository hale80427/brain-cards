#!/usr/bin/env python3
"""build_fig.py — PhysicsNet 資料流的 CSS 3D 分層板（KB-19 第四層手法 ②）

第 254 跑產出。零 JS、零 canvas、零 SVG——整張圖是 HTML 元素加 CSS transform。

判別式（KB-19 第三層）：真尺寸只准在「規格來源區」誕生，畫圖區只准引用。
網路維度逐個取自 `~/Documents/曉微論文_刀況監測ML/10_素材庫/實驗數據/程式碼/physical_resnet.py`
（2026-09-06 現讀，非繼承）。

⚠ 兩個本棒 R1 真的踩到的坑，寫在這裡免得下次重踩：

1. **只有 translateZ 不夠，六個階段會全疊在同一處互相遮住。**
   `perspective` 讓近的板放大，於是最近那塊大板把後面五個階段整個蓋掉。
   必須再給一個隨階段遞增的**垂直位移**（`--ty`），讓它變成往前下方展開的階梯。
   `dim-probe` 的參考實作是靠 `tx` 隨 i 遞增達到同一效果——它只有一條軌，
   而這張圖前三階段是雙軌，`tx` 已經被軌道位置佔用了。

2. **板上的字會爆框，而且是被 `border-radius` 靜默裁掉、不報錯。**
   13 px 的中文在 150 px 板寬裡一行約十個字。首版「ResNet-18（三視角共用）」
   十四個字直接溢出。完整敘述走頁面下方那張表，板面只放最短的識別字串。

⚠ 本檔刻意**不用 `transform: scale()`** 做窄視窗適配。
   理由：`scale()` 會把板上的中文一起縮小，而 `narrow_viewport_check.py` 的字級檢查
   只掃 SVG 的 `<text>`／`<tspan>`／`<textPath>`／`foreignObject`——**它看不到 CSS 3D 的
   HTML 文字**。參考實作 `dim-probe` 用 `scale(0.46)`，13 px 的字在 375 px 下實際是 6 px，
   而該閘 exit 0。改法＝窄視窗換一組較小的板尺寸常數，字級一律不動。
"""

import math

# @figure-spec-source
# ── 網路真尺寸（逐個對得上 physical_resnet.py 的哪一行，見行末註解）
PHYS_IN     = 8     # PhysicsNet(num_physics_features=8)
PHYS_H1     = 32    # nn.Linear(num_physics_features, 32)
PHYS_OUT    = 64    # physics_hidden_dim = 64
VIS_OUT     = 512   # vision_out_dim = resnet.fc.in_features
VIS_VIEWS   = 3     # img_ce, img_rf, img_ff
CLS_H1      = 512   # nn.Linear(total_feature_dim, 512)
CLS_H2      = 128   # nn.Linear(512, 128)
NUM_CLASSES = 4     # num_classes=4，磨耗 Level 0~3
IMG_SIDE    = 224   # dummy_imgs 的 (2, 3, 224, 224)

# ── 版面尺寸：寬視窗
PLATE_GAP_PX    = 58.0    # 相鄰階段的深度間距（z）
STAGE_DY_PX     = 84.0    # 相鄰階段的垂直錯開量——沒有它，六個階段會全疊在同一處
TRACK_TX_PX     = 116.0   # 雙軌階段時左右兩軌各自的橫向偏移
PLATE_W_BASE_PX = 150.0   # 最遠那個階段的板寬
PLATE_W_STEP_PX = 15.0    # 每往前一階段板寬增加多少（與深度同向·KB-19 踩坑 1）
PLATE_H_BASE_PX = 50.0
PLATE_H_STEP_PX = 2.0
MERGE_W_BASE_PX = 384.0   # 合流後的板寬——刻意做到橫跨兩軌，用「接住」表達合併
MERGE_W_STEP_PX = 14.0
PERSPECTIVE_PX  = 1250.0
ROT_X_DEG       = 15.0
ROT_Y_DEG       = -9.0
DECK_H_PX       = 552.0
DECK_SHIFT_PX   = 34.0     # 橫向補正（抵銷 rotateY 造成的偏移）
DECK_LIFT_PX    = -204.0  # 垂直補正（把整疊拉回視窗中央）

# ── 版面尺寸：375 px 窄視窗（換常數，不用 scale()）
N_PLATE_GAP_PX    = 34.0
N_STAGE_DY_PX     = 58.0
N_TRACK_TX_PX     = 68.0
N_PLATE_W_BASE_PX = 116.0
N_PLATE_W_STEP_PX = 9.0
N_PLATE_H_BASE_PX = 42.0
N_PLATE_H_STEP_PX = 1.0
N_MERGE_W_BASE_PX = 226.0
N_MERGE_W_STEP_PX = 9.0
N_PERSPECTIVE_PX  = 820.0
N_DECK_H_PX       = 404.0
N_DECK_SHIFT_PX   = 18.0
N_DECK_LIFT_PX    = -144.0
# @end-figure-spec-source


# @figure-spec
VIS_CONCAT = VIS_OUT * VIS_VIEWS      # 三視角特徵拼接後的維度
FUSED      = VIS_CONCAT + PHYS_OUT    # 融合層的輸入維度

TRACK_CLASS = {"vis": "tv", "phys": "tp", "one": "to"}


def stages():
    """六個階段，由遠到近＝資料流的先後。每格是 (階段名, 視覺軌, 物理軌, 軌數)。"""
    return [
        ("輸入", "三視角影像", "{} 個參數".format(PHYS_IN), 2),
        ("編碼", "ResNet-18 ×{}".format(VIS_VIEWS),
                 "{}→{}→{}".format(PHYS_IN, PHYS_H1, PHYS_OUT), 2),
        ("特徵", "{} ×{}".format(VIS_OUT, VIS_VIEWS), "{}".format(PHYS_OUT), 2),
        ("拼接", "{} ＋ {} ＝ {}".format(VIS_CONCAT, PHYS_OUT, FUSED), None, 1),
        ("壓縮", "{}→{}→{}".format(FUSED, CLS_H1, CLS_H2), None, 1),
        ("輸出", "{} 個磨耗等級".format(NUM_CLASSES), None, 1),
    ]


def merge_from():
    """第一個單軌（已合流）階段的索引——不寫死，由 stages() 自己算出來。"""
    for i, (_, _, _, tracks) in enumerate(stages()):
        if tracks == 1:
            return i
    raise SystemExit("BLOCK: stages() 裡沒有任何單軌階段")


def table_stages():
    """表格用的完整敘述——板面放不下的細節放這裡。"""
    return [
        ("輸入", "三視角影像 {}×{}".format(IMG_SIDE, IMG_SIDE),
                 "{} 個機台參數".format(PHYS_IN)),
        ("編碼", "ResNet-18（三個視角共用同一份權重）",
                 "Linear {}→{} → BN → ReLU → Dropout → Linear {}→{} → BN → ReLU".format(
                     PHYS_IN, PHYS_H1, PHYS_H1, PHYS_OUT)),
        ("特徵", "{} 維 × {} 視角".format(VIS_OUT, VIS_VIEWS),
                 "{} 維".format(PHYS_OUT)),
        ("拼接", "{} ＋ {} ＝ {} 維".format(VIS_CONCAT, PHYS_OUT, FUSED), "（已合流）"),
        ("壓縮", "Linear {}→{} → Linear {}→{}".format(FUSED, CLS_H1, CLS_H1, CLS_H2),
                 "（已合流）"),
        ("輸出", "Linear {}→{}，磨耗 Level 0–{}".format(
                     CLS_H2, NUM_CLASSES, NUM_CLASSES - 1), "（已合流）"),
    ]


def plate(cls, idx, tx, geo, stage, label):
    """一塊板。z 帶一個 rotateY 補償項，理由見下。

    `rotateY(θ)` 把橫向位移的一部分帶進視深度：`z' = x·sinθ + z·cosθ`。
    於是雙軌階段的兩塊板（`tx = ±TRACK_TX`）落在不同的 z' 上——一塊更近更大、
    一塊更遠更高——**看起來像不在同一個階段**，而它們明明是。
    `tx = ±116`、`θ = -11°` 時兩軌的 z' 差 `232·tan11° ≈ 45 px`。
    補償 `z += tx·tanθ` 讓同階段的兩塊板回到同一個視深度。
    紅色單軌板 `tx = 0`，補償為零、不受影響。
    """
    gap, dy, wbase, wstep, hbase, hstep, mbase, mstep, mfrom = geo
    z = gap * idx + tx * math.tan(math.radians(ROT_Y_DEG))
    if tx == 0.0:
        w = mbase + mstep * (idx - mfrom)
    else:
        w = wbase + wstep * idx
    return ('<div class="pl {}" style="--z:{:.0f}px;--tx:{:.0f}px;--ty:{:.0f}px;'
            '--w:{:.0f}px;--h:{:.0f}px"><b>{}</b><span>{}</span></div>').format(
        cls, z, tx, dy * idx, w, hbase + hstep * idx, stage, label)


def deck_plates(geo, tx_step):
    out = []
    for i, (stage, vis, phys, tracks) in enumerate(stages()):
        if tracks == 2:
            out.append(plate(TRACK_CLASS["vis"], i, -tx_step, geo, stage, vis))
            out.append(plate(TRACK_CLASS["phys"], i, tx_step, geo, stage, phys))
        else:
            out.append(plate(TRACK_CLASS["one"], i, 0.0, geo, stage, vis))
    return "".join(out)


def one_deck(cls, persp, deckh, shift, lift, geo, tx_step):
    return ('<div class="deck {}" style="--persp:{:.0f}px;--deckh:{:.0f}px;'
            '--rx:{:.0f}deg;--ry:{:.0f}deg;--shift:{:.0f}px;--lift:{:.0f}px" '
            'aria-hidden="true"><div class="deck-in">{}</div></div>').format(
        cls, persp, deckh, ROT_X_DEG, ROT_Y_DEG, shift, lift,
        deck_plates(geo, tx_step))


def build():
    mfrom = merge_from()
    wide_geo = (PLATE_GAP_PX, STAGE_DY_PX, PLATE_W_BASE_PX, PLATE_W_STEP_PX,
                PLATE_H_BASE_PX, PLATE_H_STEP_PX,
                MERGE_W_BASE_PX, MERGE_W_STEP_PX, mfrom)
    narrow_geo = (N_PLATE_GAP_PX, N_STAGE_DY_PX, N_PLATE_W_BASE_PX, N_PLATE_W_STEP_PX,
                  N_PLATE_H_BASE_PX, N_PLATE_H_STEP_PX,
                  N_MERGE_W_BASE_PX, N_MERGE_W_STEP_PX, mfrom)
    return (one_deck("deck-wide", PERSPECTIVE_PX, DECK_H_PX, DECK_SHIFT_PX,
                     DECK_LIFT_PX, wide_geo, TRACK_TX_PX)
            + one_deck("deck-narrow", N_PERSPECTIVE_PX, N_DECK_H_PX, N_DECK_SHIFT_PX,
                       N_DECK_LIFT_PX, narrow_geo, N_TRACK_TX_PX))


def table_rows():
    """同一批數字的無障礙文字版——deck 標 aria-hidden，讀屏與窄視窗讀者走這張表。"""
    return "".join('<tr><td>{}</td><td>{}</td><td>{}</td></tr>'.format(a, b, c)
                   for a, b, c in table_stages())
# @end-figure-spec


if __name__ == "__main__":
    print(build())
