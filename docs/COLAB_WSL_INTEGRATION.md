# WSL / Google Colab CLI 連携仕様書 (COLAB_WSL_INTEGRATION.md)

本ドキュメントは、WSL（Arch Linux）環境にセットアップ済みの `google colab cli` を活用し、Google ColabのクラウドVM（GPU/TPU）へ重いタスクをオフロードするための設計および運用手順を定義します。

---

## 1. 概要と役割分担

| 実行環境 | 得意領域・担当タスク |
|---|---|
| **ローカル (`uv` / Windows)** | PDF/EPUBテキスト抽出、目次解析、EPUBパッケージング、Antigravity APIサブエージェントによる通常翻訳。 |
| **Google Colab (WSL `colab` CLI経由)** | 将来的な大規模バッチ推論（OSSのローカルLLMを用いたオフライン一括翻訳、重いマルチモーダルOCR、挿絵のAIアップスケーリング等）。 |

---

## 2. WSL環境の前提・構成

- **ディストリビューション**: WSL 2 (任意のLinuxディストリビューション、例: Arch Linux / Ubuntu)
- **CLI実行パス**: `~/.local/bin/colab` (または `$HOME/.local/bin/colab`)
- **設定・セッション保存先**: `~/.config/colab-cli/`
- **WSL内 uv パス**: `~/.local/bin/uv` (または `$PATH` 上の `uv`)

---

## 3. `ColabBridge` モジュールの仕様 (`src/tl_ebook/colab.py`)

PythonからWSLのbashログインシェルを経由してコマンドを実行します：

```python
from tl_ebook.colab import ColabBridge

bridge = ColabBridge()

# 1. セッションステータスの確認
status = bridge.check_status()
print(status["stdout"])

# 2. 新規Colab VMでのスクリプト実行 (colab run)
# bridge.run_script("/path/to/script.py")

# 3. 既存のアクティブセッション内でのコード実行 (colab exec)
# bridge.execute_in_session(session_id="...", code="print('Hello from Colab')")
```

---

## 4. CLIコマンドでの利用

```bash
# WSL内のColab CLIステータスとアクティブセッション一覧を確認
uv run tl-ebook colab-status
```

### 注意事項・トラブルシューティング
- **OS Keyring 警告**:
  WSLヘッドレス環境下では、OAuthトークン保存用のGUI keyringが利用できないため、stderrに警告メッセージが出力される場合があります。これは正常な動作であり、コマンド自体の実行（`returncode == 0`）には影響ありません。永続化したい場合は `keyrings.alt` パッケージをWSL環境へ導入するか、`--auth=adc` を使用してください。
