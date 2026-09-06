#!/usr/bin/env python3
"""render.py — 把 build_fig.py 的產出注入模板，產生 index.html。

圖說裡的每個數字都從 build_fig 匯入，不手打（承 [[L191]]：散文裡手打的數字
在資料變動後會靜默失真，而 grep 自驗結構上照不到——因為失真的正是「要 grep 什麼」
這個認知）。
"""
import re
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import build_fig as F

HERE = pathlib.Path(__file__).parent
TPL = (HERE / "index.template.html").read_text(encoding="utf-8")

CAP_LEAD = ("兩條路徑在第四階段才合流——影像走 ResNet-18 抽出 %d 維、"
            "機台參數走多層感知器抽出 %d 維，合併成 %d 維之後只經過兩層就輸出 %d 個磨耗等級。"
            % (F.VIS_CONCAT, F.PHYS_OUT, F.FUSED, F.NUM_CLASSES))

CAP_NOTE = ("Note：六個階段的維度逐個取自 <code>physical_resnet.py</code>（2026-09-06 現讀，非繼承）。"
            "圖是 CSS <code>perspective</code> ＋ <code>translateZ</code> 做的，"
            "零 JavaScript、零 <code>&lt;canvas&gt;</code>——把頁面全部 <code>&lt;script&gt;</code> "
            "剝掉，圖一樣完整。板的大小只編碼資料流的先後，讀不出張量大小。")

CAP_SRC = ("Source：曉微論文 PhysicsNet 實作，"
           "<code>10_素材庫/實驗數據/程式碼/physical_resnet.py</code>；"
           "圖的產生器 <code>physicsnet-layers/build_fig.py</code>。")

FIGURE = ('<figure>\n<div class="figbox">%s</div>\n<figcaption>'
          '<span class="lead">%s</span>'
          '<span class="note">%s</span>'
          '<span class="src">%s</span>'
          '</figcaption>\n</figure>' % (F.build(), CAP_LEAD, CAP_NOTE, CAP_SRC))


def main():
    out = TPL
    for mark, payload in (("<!--FIG1-->", FIGURE), ("<!--TBL1-->", F.table_rows())):
        if mark not in out:
            raise SystemExit("BLOCK: 模板缺注入標記 %s" % mark)
        out = out.replace(mark, payload, 1)
    if "<!--" in out.split("</head>", 1)[1] and re.search(r"<!--(FIG|TBL)", out):
        raise SystemExit("BLOCK: 還有沒被替換掉的注入標記")
    (HERE / "index.html").write_text(out, encoding="utf-8")
    print("寫出 index.html（%d 位元組）" % len((HERE / "index.html").read_bytes()))


if __name__ == "__main__":
    main()
