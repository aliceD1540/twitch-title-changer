# 開発者向けドキュメント

このドキュメントは、Twitch Title Changer の開発者向けガイドです。

## プロジェクト概要

Twitch Title Changer は、配信のタイトルやゲーム情報を効率的に管理・変更するツールです。

### アーキテクチャ

```
┌─────────────────────────────────────────┐
│         GUI Layer (PySimpleGUI)         │
│         src/gui/app.py                  │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│     Application Logic Layer              │
│  - Event Handling                       │
│  - User Input Validation                │
└──────────────────┬──────────────────────┘
                   │
       ┌───────────┴────────────┐
       │                        │
       ▼                        ▼
┌─────────────────┐    ┌──────────────────┐
│  Config Layer   │    │   API Layer      │
│ src/config/*    │    │ src/api/*        │
│ - Models       │    │ - TwitchClient   │
│ - Loader       │    │ - Exceptions     │
└─────────────────┘    └──────────────────┘
       │                        │
       └───────────┬────────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │   External APIs     │
        │  - Twitch API       │
        │  - File System      │
        └─────────────────────┘
```

## モジュール解説

### src/config

設定管理を担当します。

- **models.py**: `AppConfig`, `GameConfig` データクラス
  - 型安全な設定の表現
  - 辞書との相互変換メソッド
  - ビジネスロジック（ソート、最大値取得など）

- **loader.py**: `ConfigLoader` クラス
  - JSON ファイルからの読み込み
  - ファイルへの保存
  - エラーハンドリング

### src/api

Twitch API との連携を担当します。

- **twitch_client.py**: `TwitchClient` クラス
  - 初期化と認証
  - ゲーム検索
  - チャンネル情報取得・更新
  - トークンのリフレッシュ

- **exceptions.py**: カスタム例外定義
  - `TwitchAPIError`: 基底例外
  - `TwitchAuthenticationError`: 認証エラー
  - `TwitchRateLimitError`: レート制限エラー
  - `TwitchConnectionError`: 接続エラー

### src/gui

ユーザーインターフェースを担当します。

- **app.py**: `TwitchTitleChangerApp` クラス
  - メインアプリケーションロジック
  - ウインドウ管理
  - イベントハンドリング
  - ユーザー操作の処理

### src/utils

ユーティリティ関数を提供します。

- **logger.py**: `get_logger` 関数
  - ロギング設定
  - ファイルハンドラとコンソールハンドラ

## 開発ワークフロー

### 新機能の追加

1. **機能の仕様を定義**
   - どのレイヤーに属するか決定
   - 入出力を明確にする

2. **モデルを追加（必要に応じて）**
   ```python
   # src/config/models.py に新しいデータクラスを追加
   @dataclass
   class NewFeatureConfig:
       ...
   ```

3. **API メソッドを追加**
   ```python
   # src/api/twitch_client.py に新しいメソッドを追加
   async def new_api_method(self, ...):
       ...
   ```

4. **GUI に UI を追加**
   ```python
   # src/gui/app.py にイベントハンドラを追加
   if event == "新機能ボタン":
       ...
   ```

5. **テストを追加**
   ```python
   # tests/test_feature.py に単体テストを追加
   class TestNewFeature(unittest.TestCase):
       ...
   ```

### バグ修正

1. **バグの再現条件を確認**
2. **テストを追加**（修正前にテストが失敗することを確認）
3. **コードを修正**
4. **テストが通ることを確認**

### コード品質の保証

```bash
# ユニットテストの実行
python -m pytest tests/ -v

# 型チェック（オプション）
mypy src/

# コード整形（オプション）
black src/ tests/

# リント（オプション）
flake8 src/ tests/
```

## 非同期処理の注意点

- `await` を使用している場合は、必ず `async def` 関数の中で使用する
- GUI イベントループとの競合を避けるため、重い処理は `asyncio.run()` で実行
- トークンのリフレッシュなどは自動で行われる

### 例

```python
# GUI イベントハンドラ
if event == "Twitchに反映":
    # 非同期処理を実行
    success = await self.twitch_client.update_channel_information(...)
```

## ロギング

`get_logger()` を使用してログを出力できます：

```python
from src.utils.logger import get_logger

logger = get_logger(__name__)

logger.info("情報メッセージ")
logger.warning("警告メッセージ")
logger.error("エラーメッセージ")
```

ログは以下に出力されます：
- コンソール: stdout に出力
- ファイル: `logs/twitch_title_changer.log` に出力

## エラーハンドリング

API 層では専門的な例外を投げます：

```python
from src.api.exceptions import TwitchAuthenticationError, TwitchConnectionError

try:
    await client.authenticate(...)
except TwitchAuthenticationError as e:
    # 認証エラー処理
    logger.error(f"Authentication failed: {e}")
except TwitchConnectionError as e:
    # 接続エラー処理
    logger.error(f"Connection failed: {e}")
```

GUI 層では例外をキャッチしてユーザーに通知します：

```python
try:
    await self._handle_regist_to_twitch(game)
except Exception as e:
    sg.popup_error("エラーが発生しました", f"{e}")
```

## テストの実行

### すべてのテストを実行

```bash
python -m pytest tests/ -v
```

### 特定のテストを実行

```bash
python -m pytest tests/test_config.py::TestAppConfig::test_add_game -v
```

### カバレッジレポートを生成

```bash
python -m pytest tests/ --cov=src --cov-report=html
```

## パフォーマンスの考慮

- Twitch API 呼び出しはキャッシングを活用
- UI の更新はできるだけ効率的に
- 大量のデータ処理は非同期で

## セキュリティの注意点

- **認証情報**: `config.json` にシークレットを保存しないようにする
- **トークン管理**: リフレッシュトークンは安全に保管
- **ユーザー入力**: 検証とサニタイズを実施
- **API キー**: リポジトリにコミットしない

## リリース手順（今後）

1. バージョン番号を更新
2. CHANGELOG を記述
3. タグを作成
4. リリースノートを作成

## 参考資料

- [Twitch API ドキュメント](https://dev.twitch.tv/docs/api)
- [twitchAPI ライブラリ](https://github.com/Teekeks/pyTwitchAPI)
- [PySimpleGUI ドキュメント](https://pysimplegui.readthedocs.io/)
- [asyncio ドキュメント](https://docs.python.org/ja/3/library/asyncio.html)

## よくある質問

**Q: 新しいエラーハンドリングの例は？**

A: 見本コードは `src/api/twitch_client.py` の各メソッドを参照してください。

**Q: テストはどのように書く？**

A: `tests/test_config.py` を参照してください。

**Q: GUI の新しいウインドウを追加したい場合は？**

A: `src/gui/app.py` に新しいメソッド `_open_xxx_window()` を追加します。

## 連絡先・サポート

開発に関する質問や提案は GitHub Issues でお願いします。
