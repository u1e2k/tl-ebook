# テキスト抽出アルゴリズム仕様書 (EXTRACTOR_SPEC.md)

本ドキュメントは、PDFおよびEPUBから段落構造・ハイフネーションを欠損なく高精度に抽出する `PdfExtractor` のアルゴリズム仕様を定義します。

---

## 1. 課題と背景

市販の電子書籍PDFやEPUBを単純に `extract_text()` で抽出すると、以下の深刻な問題が発生します：

1. **行末ハイフネーションの分断**:
   - `seventeenth-` と `century` が別々の単語に分断され、`seventeenth- century` のようなゴミが混入する。
2. **段落境界の喪失**:
   - 行ごとに改行が入るため、どこからどこまでが1つの段落（パラグラフ）なのか判別不能になる。
3. **見開き（奇数・偶数ページ）のマージン差**:
   - 印刷書籍の製本仕様上、奇数ページ（右ページ）と偶数ページ（左ページ）で「のど（綴じ側）」と「小口（外側）」の余白が交互に反転する。
   - そのため、固定の絶対X座標（例: `x0 > 16.0`）でインデント判定を行うと、偶数ページで通常行がすべてインデント扱いになり、1行ごとに段落が細切れになる。
4. **PDF内部ストリームの走査順序（Y座標）**:
   - PDF生成エンジンによっては、テキストオブジェクトがページの下から上に向かって配置されている場合がある。

---

## 2. 抽出アルゴリズムの解法

`src/tl_ebook/extractor.py` では、上記を以下の多段階パイプラインで解決しています。

### ステップ1: テキストランの取得とY座標グルーピング
1. `pypdf.PdfReader` の `page.extract_text(visitor_text=...)` を使用し、テキスト断片（run）のテキスト内容、開始X座標（`tm[4]`）、Y座標（`tm[5]`）を取得。
2. ページ内のY座標の増加方向（上から下）を基準にソート。
3. 同一の行（`abs(y0 - curr_y) <= 3.0` pt）に存在するランをX座標順に並び替え、1つの「行（Line）」として結合。

### ステップ2: 動的ベースマージンの自動検出（最重要）
奇数・偶数ページのマージン差を吸収するため、ページ内の全行の `x0`（左端位置）を集計します。

```python
from collections import Counter

# ページ内で最も頻繁に出現する x0（通常行の左マージン）をベースマージンとする
x0_counts = Counter(round(l["x0"], 1) for l in lines)
base_x0 = x0_counts.most_common(1)[0][0]

# 各行の相対インデントを算出
for l in lines:
    l["indent"] = l["x0"] - base_x0
```

- **奇数ページ**: `base_x0 = 0.0 pt`, インデント行 = `16.0 pt` (`indent = 16.0`)
- **偶数ページ**: `base_x0 = 624.0 pt`, インデント行 = `640.0 pt` (`indent = 16.0`)
- **判定**: `indent >= 10.0 pt`（約16pt字下げ）であれば、**確実に新しい段落の開始行**と判定！

### ステップ3: 行末ハイフネーションの自動修復
段落継続行を連結する際、末尾のハイフンを検知して修復します。

```python
if cur_p.endswith("-"):
    # ハイフンを除去して次の単語を直接結合（例: seventeenth- + century -> seventeenth-century）
    cur_p = cur_p[:-1] + next_line_text
else:
    cur_p += " " + next_line_text
```

### ステップ4: ランニングヘッダー・フッターの除外
ページ番号（数字のみの行）や、ヘッダーに印刷されている書名（`Visual Thinking`）、著者名（`Temple Grandin`）、章タイトルは正規表現とストップワードリストにより自動スキップします。

---

## 3. 出力データ構造 (`src_en/*.json`)

抽出されたデータは、以下のシンプルなJSON形式で保存されます：

```json
[
  {
    "id": "01_chapter1_p01",
    "en": "We come into the world without words. We see light, recognize faces, differentiate colors and patterns..."
  },
  {
    "id": "01_chapter1_p02",
    "en": "We assume that the dominance of language forms not only the foundation of how we communicate..."
  }
]
```

- `id`: `<prefix>_p<index:02d>` 形式。翻訳パイプラインおよび対訳テーブルの主キーとなる。
- `en`: ハイフネーションが修復され、文頭から文末まで連結された純粋な段落テキスト。
