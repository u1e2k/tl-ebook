# 翻訳パイプライン仕様書 (TRANSLATION_PIPELINE.md)

本ドキュメントは、**tl-ebook** におけるスタイルガイドの適用、用語集管理、およびサブエージェントによる並列バッチ翻訳（ファンアウト）の設計仕様を定義します。

---

## 1. 翻訳設計の基本方針

機械的な直訳調（「〜という事実」「〜の重要性についての認識」「〜によってもたらされた」など）を完全に排除し、**著者の肉声・現場主義・情熱が伝わる自然な日本語**として訳出します。

### スタイルルール (`references/style_guide.md`)
- **一人称**: 「私」
- **文体**: 「〜である／〜だ」（常体）を基本とし、問いかけでは自然に「〜だろうか」を使用。
- **トーン＆マナー**:
  - 飾らない、直截的で率直な現場の技術者目線。
  - スーツ組（経営陣・事務方）への批評と、手を動かす職人・技術屋への深い敬意。
  - 頭の中の映像（Google画像検索、ショート動画、設計図、設備の細部）を克明に描写する解像度の維持。

### 用語集の管理 (`references/glossary.json`)
主要な概念や専門用語は、プロジェクト全体でブレがないよう定訳を定義しています：
- `Visual Thinker`: 視覚思考者（ビジュアル・シンカー）
- `Object Visualizer`: 物体視覚思考者（オブジェクト・ビジュアライザー／画像思考者）
- `Spatial Visualizer`: 空間視覚思考者（スペーシャル・ビジュアライザー／パターン思考者）
- `Verbal Thinker`: 言語思考者（バーバル・シンカー）
- `Screened out`: ふるい落とされる／選別の網からこぼれ落とされる
- `Clever engineering department`: 才気あふれる現場技術部門／腕利きの職人部門
- `Neurodiversity`: ニューロダイバーシティ（神経多様性）
- `Shop class`: 木工・金工（工作）の実習クラス

---

## 2. サブエージェント並列翻訳（ファンアウト）仕様

大規模書籍（全10章、英語10万語以上）を一括翻訳する際、1つのセッションで逐次処理すると数時間かかります。
Antigravity環境では、**章ごとに独立したサブエージェントを並行起動（ファンアウト）** することで、わずか20〜30分で完了させます。

### サブエージェントの呼び出しプロトコル
```python
invoke_subagent(
    TypeName="self",
    Role="Chapter N Translator",
    Model="inherit",
    Prompt="""
    Translate Chapter N of "Visual Thinking" into Japanese.
    - Source: src_en/0N_chapterN.json
    - Style Guide: references/style_guide.md
    - Glossary: references/glossary.json
    - Output: dist/ja_md/0N_chapterN.md
    ...
    """
)
```

### 並行実行のベストプラクティス
1. **各章の独立性**:
   - 各サブエージェントは自章の `src_en/*.json` のみを読み込み、対応する `dist/ja_md/*.md` を作成する。他章のファイルには一切触れない。
2. **リアクティブ通知の活用**:
   - 親エージェント側で完了をポーリングしない。サブエージェントの `send_message` による完了通知を待機する。
3. **プロセスクリーンアップの徹底**:
   - 全サブエージェントの完了後、`manage_subagents(Action="kill_all")` を実行し、バックグラウンドセッションを確実にクリーンアップする。

---

## 3. 翻訳Markdownの標準フォーマット (`dist/ja_md/*.md`)

生成されるMarkdownファイルは、**Kindle読書用**と**推敲・校正用**の両方に対応する二部構成とします。

```markdown
# 第X章：章タイトル（Chapter X: Original Title）

---

## 日本語訳全文

段落1の日本語訳テキスト...

段落2の日本語訳テキスト...

（以下、通読用の完全な日本語本文が空行区切りで続く）

---

## 日英対訳・段落詳細

### 段落 1 [0X_chapterX_p01]
- **EN**:
  > Original English paragraph text...
- **JA**:
  > 段落1の日本語訳テキスト...

### 段落 2 [0X_chapterX_p02]
- **EN**:
  > Original English paragraph text...
- **JA**:
  > 段落2の日本語訳テキスト...
```

- **EPUBビルダーとの連携**:
  `EpubBuilder` は正規表現 `r"## 日本語訳全文\s*(.*?)(?=\n---\n|## 日英対訳|$)"` によって「日本語訳全文」のみを自動抽出し、EPUBの各章本文としてパッケージ化します。
