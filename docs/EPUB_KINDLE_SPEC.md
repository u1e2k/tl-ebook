# Kindle対応EPUBビルダー仕様書 (EPUB_KINDLE_SPEC.md)

本ドキュメントは、Amazon Kindle（Kindle Paperwhite/Oasis/Scribe、Send to Kindle、iOS/Android Kindleアプリ）で快適に読書でき、**表紙サムネイルを100%確実に表示させるためのEPUB生成仕様**を定義します。

---

## 1. Kindleで表紙サムネイルが表示されない問題と解決策（黄金ルール）

Send to Kindleの変換サーバー（Amazon KindleGenパイプライン）は、通常のEPUBリーダーに比べて極めて厳格なメタデータチェックを行っており、**1箇所でも要件を満たさないと表紙サムネイルが消滅（白紙・デフォルト表紙化）**します。

### 表紙表示の4大黄金ルール

| 項目 | 必須仕様 | 理由・影響 |
|---|---|---|
| **1. `<spine>` の先頭配置** | `<spine>` の最先頭に `<itemref idref="cover" linear="no"/>` を配置する。 | Kindleは spine の先頭アイテムがカバーページでないとサムネイル抽出をスキップする。`nav` や本文から始まると表紙が消える。 |
| **2. `<guide>` の後方互換宣言** | `<package>` 直下に `<guide><reference type="cover" title="Cover" href="cover.xhtml"/></guide>` を記述する。 | Send to KindleはEPUB 3でも内部でEPUB 2互換の `<guide>` タグを最優先で参照してサムネイル画像を切り出す。 |
| **3. ASCII識別子** | `<dc:identifier id="id">tl-ebook-visual-thinking-ja</dc:identifier>` | 識別子やIDに日本語（マルチバイト文字）が含まれると、Kindleの内部パーサーがクラッシュしメタデータ抽出に失敗する。必ず英数字・ハイフンのみとする。 |
| **4. カバー画像メタデータ** | `<metadata>` に `<meta name="cover" content="cover-img"/>`<br>`<manifest>` に `id="cover-img"` `properties="cover-image"` | EPUB 2形式の `<meta name="cover">` と EPUB 3形式の `properties="cover-image"` を両方宣言するハイブリッド構成が必須。 |

### `src/tl_ebook/builder.py` における実装コード
```python
# 1. 表紙画像の登録
if cover_image_bytes:
    self.book.set_cover("cover.jpeg", cover_image_bytes, create_page=True)

# 2. ASCII識別子の保証
self.book.set_identifier("tl-ebook-visual-thinking-ja")

# 3. spineの最先頭に "cover" を配置
spine_items = []
if self.has_cover:
    spine_items.append("cover")
spine_items.append("nav")
spine_items.extend(self.chapters)
self.book.spine = spine_items

# 4. guide要素の明示的付与
if self.has_cover:
    self.book.guide = [{"type": "cover", "title": "Cover", "href": "cover.xhtml"}]
```

---

## 2. 日本語タイポグラフィCSS設計

Kindle端末の白黒E-ink画面および高解像度スマートフォン画面の両方で視認性を最大化するCSS（`EPUB/style/nav.css`）を採用しています：

```css
@charset "UTF-8";
body {
    /* 主要OS・Kindle内蔵フォントへのフォールバック */
    font-family: "Hiragino Kaku Gothic ProN", "Yu Gothic", "Meiryo", sans-serif;
    line-height: 1.85;        /* 読みやすいゆったりした行間 */
    letter-spacing: 0.03em;   /* 和文に最適な字間 */
    margin: 5%;
    color: #1a1a1a;
}
h1 {
    font-size: 1.6em;
    font-weight: bold;
    border-bottom: 2px solid #333;
    padding-bottom: 0.3em;
    margin-top: 1.5em;
    margin-bottom: 1em;
    page-break-before: always; /* 章の開始で必ず改ページ */
}
h2 {
    font-size: 1.3em;
    font-weight: bold;
    margin-top: 1.4em;
    margin-bottom: 0.8em;
    color: #2b2b2b;
}
h3 {
    font-size: 1.15em;
    font-weight: bold;
    margin-top: 1.2em;
    margin-bottom: 0.6em;
    color: #444;
}
p {
    margin-top: 0;
    margin-bottom: 1.2em;
    text-indent: 1em;         /* 日本語標準の1字下げ */
    text-align: justify;      /* 両端揃え（ジャスティフィケーション） */
}
blockquote {
    margin: 1em 1.5em;
    padding: 0.5em 1em;
    border-left: 3px solid #ccc;
    color: #555;
    background-color: #f9f9f9;
}
```

---

## 3. 目次・ナビゲーション構造

- **EPUB 3 ナビゲーションドキュメント (`nav.xhtml`)**:
  最新の電子書籍リーダー向けHTML5目次。
- **EPUB 2 NCX (`toc.ncx`)**:
  古いKindle端末や従来のEPUBリーダー向けのXML目次。

`builder.py` では `self.book.toc = tuple(self.chapters)` とすることで、両形式の目次が完全一致で自動ビルドされます。
