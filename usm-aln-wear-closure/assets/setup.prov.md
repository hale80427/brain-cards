## spec
id: usm-drill-setup｜tier: main
規格檔：`/private/tmp/usm-fig/setup.spec.yaml`（節點 5／邊 4／不變量 1〔top→bottom 順序〕／未覆蓋 4）

## 分格盲讀
讀者：agy（Gemini 3.7 Flash (High)）｜日期：2026-08-30｜3×2 重疊格·重疊 0.3·放大 2.4×
逐格結論（r3）：6 格中 **3 格 `NOTHING WRONG`**、1 格空白（橫式構圖下的裁切偽影）、
2 格報**同一件事**＝剖面線方向不交替。**沒有任何新的物理事實錯誤。**
迭代歷程：r1 → r2 → r3，收斂於 r3。
- r1：變幅桿畫成中空、孔已穿透而鑽尖在上方、缺中心線 → 三項皆由 agy 抓到、主 session 3× 裁切親驗屬實
- r2：修好上述三項，**但引線標註退化成流程方塊圖、換能器剖面消失、`Through Hole` 標籤指向不存在的孔**
  ⇒ 追因發現 **spec 自相矛盾**（同時要求板材實心與有 Through Hole 節點），已拿掉該節點
- r3：三項物理錯誤全修、引線標註與換能器剖面恢復。**spec 內判準 100% 通過。**

## 規格外缺陷
（2026-08-30 彥皓 V0：規格外真缺陷記進附註，不回頭修）

1. **相鄰件剖面線方向不交替**。ISO 128／ASME Y14 要求裝配剖視圖中相鄰不同件用 ±45° 交替或不同間距，
   本圖的外殼、變幅桿、疊層板、夾頭本體全部同為 +45°、同間距。
   ⚠ **這一項要求過三輪、三輪都沒修** ⇒ 判定為 **Sol 在這一格的能力邊界**，不是提示不夠。
2. 壓電疊層第 6 層同時有斜線與點狀紋理，與其上五層的交替規律不一致（輕微）。

## 未覆蓋判準
`seen_by: none` 共 4 項，**不得標 ✅，只能標「未覆蓋」**：
- `axial vibration arrows`（垂直雙箭頭）——**實際上被 agy 讀到且描述正確**，但它屬領域規約類，
  本協定不把「agy 這次看到了」升格成「有覆蓋」
- `section hatching on the plate`（同上）
- `鑽頭長徑比`（連續量，沒有讀者量得了）
- `空間可行性`（連續量，同上）

## 生成資訊
prompt：由 `figspec.py prompt setup.spec.yaml` 生成（結構逐字寫死＋4 條 r2/r3 修正 annotation）
模型：`gpt-5.6-sol`（`codex-cli 0.144.6`）｜通道：`sol-imagegen`（spec 閘＋逐發記帳＋單發上限 3）
日期：2026-08-30｜記帳：`~/.cache/sol-imagegen.jsonl`（label `usm-article-setup-r1/r2/r3`）
`figspec check`：**exit 2（OCR 覆蓋不均·量不到）**——4 個標籤 100% 命中證明 OCR 讀得動，
`AlN Plate 4.0 mm` 命中 1/5；主 session 與 agy 雙讀確認該標籤**在圖上**，屬 OCR 漏讀。
