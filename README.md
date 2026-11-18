# tl-ebook 📚

**tl-ebook** は、英語の洋書・電子書籍（PDF / EPUB）を高精度に構造解析し、プロフェッショナル品質の日本語翻訳を経て、Amazon Kindle等で快適に読める美しい日本語EPUBを自動生成するためのパイプライン・CLIツールです。

---

## 主な特徴

- ⚡ **超高速なパッケージ管理**: `uv` による依存関係・仮想環境の即座なセットアップと再現性。
- 🔍 **高精度な書籍構造抽出 (`PdfExtractor`)**:
  - 見開き左右ページで交互に変わるマージン差（のど・小口オフセット）を動的に自動吸収。
  - 16ptインデント判定による正確な段落境界認識と、行末ハイフネーション（`seventeenth-century`等）の自動修復。
  - PDF目次（アウトライン・ブックマーク）からの章・節・ページ範囲の自動マッピング。
- 🌐 **AI並行翻訳パイプライン (`TranslationManager`)**:
  - 文体スタイルガイド（常体・一人称「私」・現場目線）と用語集（`glossary.json`）の厳格な統一。
  - サブエージェントを活用した全章並列翻訳（ファンアウト）により、単行本1冊分（数十万字）を20〜30分で一括翻訳。
  - 通読用の「日本語訳全文」と、検証・推敲用の「日英対訳詳細」を両立したMarkdown出力。
- 📱 **Kindle完全対応 EPUBビルダー (`EpubBuilder`)**:
  - Send to Kindle で表紙サムネイルが消える問題を完全に解消（`<guide>`、`<spine>`先頭配置、ASCII識別子、EPUB3カバーメタデータ）。
  - 日本語タイポグラフィ（美しい行間、字下げ、フォントフォールバック、改章制御）に最適化されたCSS。
- ☁️ **WSL / Google Colab CLI 連携基盤 (`ColabBridge`)**:
  - WSL（Arch Linux等）上の `google colab cli` とシームレスに交信し、大量バッチ処理やGPU推論をクラウドVMへオフロード可能。

---

## ディレクトリ構成

```text
tl-ebook/
├── pyproject.toml         # uv プロジェクト設定・依存関係・CLIエントリーポイント
├── uv.lock                # 確定済み依存関係スナップショット
├── .gitignore             # 著作物・抽出生データ・成果物の除外設定
├── README.md              # 本ドキュメント
├── docs/                  # 各種設計・仕様書（Antigravity/開発者向け）
│   ├── ARCHITECTURE.md            # システム全体設計・アーキテクチャ
│   ├── EXTRACTOR_SPEC.md          # 高精度PDF/EPUB抽出アルゴリズム仕様
│   ├── TRANSLATION_PIPELINE.md    # 翻訳パイプライン・並行処理仕様
│   ├── EPUB_KINDLE_SPEC.md        # Kindle完全対応EPUB生成仕様
│   └── COLAB_WSL_INTEGRATION.md   # WSL / Google Colab CLI 連携仕様
├── references/            # 翻訳リソース（Git管理対象）
│   ├── glossary.json      # 専門用語統一辞書
│   └── style_guide.md     # 著者ボイス・文体ガイドライン
├── src/
│   └── tl_ebook/          # ツール本体
│       ├── __init__.py
│       ├── cli.py         # Click CLI エントリーポイント
│       ├── extractor.py   # PDF/EPUB構造化抽出モジュール
│       ├── translator.py  # 用語集・対訳Markdown管理モジュール
│       ├── builder.py     # Kindle最適化EPUBビルダー
│       └── colab.py       # WSL/Colab連携ブリッジ
├── src_en/                # 【gitignore】抽出された章別原文JSONデータ
└── dist/                  # 【gitignore】生成成果物
    ├── ja_md/             # 各章の日本語訳・対訳Markdownファイル
    └── ja_epub/           # ビルドされた完成版日本語EPUBファイル
```

---

## セットアップ手順

### 必要環境
- Python 3.10 以上
- [uv](https://github.com/astral-sh/uv) (インストール済みであれば即座に使用可能)

### インストール
```bash
# 依存関係の同期（仮想環境 .venv を自動構築）
uv sync

# 開発モード（editable）として反映
uv pip install -e .
```

---

## 基本的な使い方（CLIコマンド）

### 1. 目次とページ番号の確認 (`toc`)
ソースPDFの目次アウトラインと各章の開始ページ一覧を表示します。
```bash
uv run tl-ebook toc "path/to/source.pdf"
```

### 2. 書籍の全章・段落を一括抽出 (`extract`)
動的インデント判定を行い、全章を構造化JSONとして `src_en/` に出力します。
```bash
uv run tl-ebook extract "path/to/source.pdf" -o src_en
```

### 3. 日本語EPUBのビルド (`build`)
`dist/ja_md/` 内の翻訳済みMarkdownを結合し、Kindle完全対応のEPUBをビルドします。
原著EPUB（または画像ファイル）を指定すると、自動で表紙（Cover）が組み込まれます。
```bash
uv run tl-ebook build --cover "path/to/source.epub"
```
- デフォルト出力先: `dist/ja_epub/Visual_Thinking_ja.epub`

### 4. WSL Google Colab CLI のステータス確認 (`colab-status`)
WSL内の `colab` コマンドとの疎通やアクティブセッションを確認します。
```bash
uv run tl-ebook colab-status
```

---

## 詳細仕様ドキュメント

今後の拡張やAntigravityによる機能改善の詳細は、[docs/](docs/) 配下の各種仕様書をご参照ください：
- 📐 [システム全体アーキテクチャ](docs/ARCHITECTURE.md)
- 🔬 [PDF/EPUB抽出アルゴリズムの仕様](docs/EXTRACTOR_SPEC.md)
- ✍️ [翻訳パイプラインとサブエージェント並列運用](docs/TRANSLATION_PIPELINE.md)
- 📖 [Kindle向けEPUB仕様と表紙表示の黄金ルール](docs/EPUB_KINDLE_SPEC.md)
- 🚀 [WSL / Google Colab CLI 連携手順](docs/COLAB_WSL_INTEGRATION.md)
