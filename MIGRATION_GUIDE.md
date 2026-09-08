# マイグレーションガイド

このドキュメントは、旧バージョン（v1.x）から新バージョン（v2.0）へのマイグレーション方法を説明しています。

## 概要

v2.0 はコード品質とメンテナンス性を大幅に改善したリファクタリング版です。以下の点が改善されています：

- **プロジェクト構造**: モジュール化され、拡張が容易になりました
- **型安全性**: 型ヒントが追加されました
- **エラー処理**: より詳細で構造化されたエラー処理
- **テスト**: 単体テストが追加されました
- **ロギング**: ファイルとコンソールに出力されるロギングシステム

## 変更点

### ファイル構成

**旧バージョン:**
```
main.py          # グローバル変数、混在した責任
gui.py           # GUI ロジック + API 呼び出し
config.json      # 認証情報を含む
```

**新バージョン:**
```
src/
  ├── config/    # 設定管理モジュール
  ├── api/       # Twitch API ラッパー
  ├── gui/       # GUI アプリケーション
  └── utils/     # ユーティリティ
main.py      # エントリーポイント
```

### 起動方法

**旧バージョン:**
```bash
python gui.py
```

**新バージョン:**
```bash
python main.py
```

### 設定ファイルの形式

基本的には変わっていませんが、以下の改善があります：

- `ClientId` / `SecretId`: 今後は環境変数による外部化を推奨
- `Games`: より厳密な型チェック
- `Token` / `RefreshToken`: 自動保存・管理

## マイグレーション手順

### 1. 新しいブランチから開始

すでにリファクタリング用ブランチ `refactor/restructure-codebase` が作成されています。

```bash
git branch -v  # ブランチを確認
```

### 2. 既存の config.json をバックアップ

```bash
cp config.json config.json.backup
```

### 3. 新しいアプリケーションの起動

```bash
python main.py
```

### 4. 動作確認

- 認証が正しく機能するか
- ゲーム情報が正しく読み込まれるか
- Twitchへの反映が正しく機能するか

## API の変更

### 旧バージョン

```python
import main
config = main.config

# ゲームリストを取得
game_list = main.get_game_list()

# ゲームを検索
results = main.search_games("Minecraft")

# 配信情報を更新
await main.change_broadcaster_info({
    'BroadcasterName': 'username',
    'GameId': '123',
    'Title': 'My Stream',
    'Tags': 'tag1,tag2'
})
```

### 新バージョン

```python
from src.config.loader import ConfigLoader
from src.api import TwitchClient
from src.config.models import GameConfig

# 設定を読み込む
loader = ConfigLoader("./config.json")
config = loader.load()

# Twitch クライアントを初期化
client = TwitchClient(config.client_id, config.secret_id)
await client.initialize()

# 認証
access_token, refresh_token = await client.authenticate()

# ゲームを検索
results = await client.search_games("Minecraft")

# 配信情報を更新
success = await client.update_channel_information(
    broadcaster_id="123456",
    game_id="123",
    title="My Stream",
    tags=["tag1", "tag2"]
)

# 終了
await client.close()
```

## 既存コードとの互換性

旧 `main.py` と `gui.py` は以下の理由で削除または改名されました：

- `main.py` → `src/api/twitch_client.py`, `src/config/loader.py` に分割
- `gui.py` → `src/gui/app.py` にリファクタリング

これらは以下のディレクトリに保存されています：
- `main_old.py` (旧 main.py)
- `gui_old.py` (旧 gui.py)

必要に応じて参照できますが、新バージョンの使用を推奨します。

## トラブルシューティング

### エラーが発生する場合

ログファイルを確認してください：

```bash
cat logs/twitch_title_changer.log
```

### 認証が失敗する場合

1. `config.json` の `ClientId` と `SecretId` が正しいか確認
2. Twitch Developer Console でアプリケーションが登録されているか確認
3. アプリケーションのスコープが正しいか確認（`CHANNEL_MANAGE_BROADCAST` が必要）

### ゲーム情報が見つからない場合

- ゲーム名のスペル、大文字小文字を確認
- Twitch API の検索仕様を確認（完全一致ではなく部分一致）

## サポート

問題が発生した場合は、以下の手順で報告してください：

1. ログファイルを確認
2. コマンドラインで詳細ログを有効にして実行
3. Issue を作成して、ログ内容を含める

## まとめ

v2.0 はより堅牢で保守しやすいコード構造となっています。既存の `config.json` ファイルは互換性を保っているため、データの移行は不要です。

新しいプロジェクト構造とモジュール化により、今後の機能追加やバグ修正がより容易になります。
