# Twitch Title Changer - リファクタリング版

Twitchの配信タイトルを効率的に管理・変更するツールです。複数のゲームタイトルを事前に登録し、ワンクリックでTwitchの配信情報を更新できます。

## 新機能・改善点

### リファクタリング v2.0

- ✅ **モジュール化**: プロジェクト構造を整理（`src/config`, `src/api`, `src/gui`, `src/utils`）
- ✅ **型安全性**: 型ヒントを追加、Dataclass による型安全な設定管理
- ✅ **エラーハンドリング**: 統一されたエラー処理と例外定義
- ✅ **ロギング**: ファイル出力とコンソール出力対応のロギングシステム
- ✅ **テスト**: 設定管理の単体テストを追加
- ✅ **非同期処理**: asyncio による適切な非同期処理の管理
- ✅ **API ラッパー**: Twitch API の統一されたインターフェース
- ✅ **セキュリティ**: 環境変数対応への準備

## 必要なパッケージ

- PySimpleGUI >= 4.60
- twitchAPI >= 3.11
- その他（詳細は requirements.txt を参照）

## インストール

### WSL/Linux ユーザー向け（推奨）

自動セットアップスクリプトを使用：

```bash
chmod +x setup_wsl.sh
./setup_wsl.sh
```

このスクリプトが以下を自動で行います：
- Python 3 の確認
- 日本語フォント（Noto Sans CJK）のインストール
- ロケール設定
- Python 依存パッケージのインストール

### 手動インストール

```bash
pip install -r requirements.txt
```

### WSL 環境での文字化け対策

WSL で日本語が豆腐（□）のように表示される場合：

```bash
# ロケール設定
export LANG=ja_JP.UTF-8
export LC_ALL=ja_JP.UTF-8

# 日本語フォントをインストール
sudo apt install fonts-noto-cjk

# アプリケーション実行
python3 main_new.py
```

詳細は [WSL_GUIDE.md](WSL_GUIDE.md) を参照してください。

## 設定

### config.json の作成

1. `config.json.sample` をコピーして `config.json` を作成
2. Twitch Developer Console から取得した以下の情報を入力：
   - `ClientId`: クライアントID
   - `SecretId`: シークレットID
3. ゲーム情報を `Games` 配列に追加（オプション）

```json
{
    "ClientId": "your_client_id",
    "SecretId": "your_secret_id",
    "Games": [
        {
            "GameId": "686119195",
            "GameName": "Armored Core VI: Fires of Rubicon",
            "Title": "【ほぼ初AC】ARMORED CORE VI【ヘタレイヴン】",
            "Priority": 0,
            "Tags": "日本語,初見"
        }
    ]
}
```

## 使い方

### 起動コマンド

**標準的な実行:**
```bash
python3 main_new.py
```

**WSL/Linux 環境:**
```bash
LANG=ja_JP.UTF-8 python3 main_new.py
```

**環境変数を完全に指定する場合:**
```bash
LANG=ja_JP.UTF-8 LC_ALL=ja_JP.UTF-8 PYTHONIOENCODING=utf-8 python3 main_new.py
```

### 基本的な操作

1. **Twitch ユーザー名を入力して認証**
   - 初回実行時はブラウザで認証画面が開きます
   - トークンは自動保存されます

2. **ゲーム情報を管理**
   - **作成**: 新しいゲーム配信情報を追加
   - **編集**: 既存の情報を修正
   - **削除**: 不要な情報を削除
   - **↑/↓**: 優先度順序を変更

3. **Twitchに反映**
   - ゲームを選択して「Twitchに反映」をクリック
   - 配信タイトル、ゲーム、タグが更新されます

### トラブルシューティング

**文字化け（豆腐）が発生する場合:**
- [WSL_GUIDE.md](WSL_GUIDE.md) を参照してください
- 通常は `LANG=ja_JP.UTF-8` を設定することで解決します

**その他のエラー:**
- ログファイルを確認: `cat logs/twitch_title_changer.log`

## プロジェクト構造

```
twitch-title-changer/
├── src/
│   ├── __init__.py
│   ├── config/              # 設定管理
│   │   ├── __init__.py
│   │   ├── models.py        # 設定データクラス
│   │   └── loader.py        # 設定ファイル読み書き
│   ├── api/                 # Twitch API
│   │   ├── __init__.py
│   │   ├── twitch_client.py # API ラッパー
│   │   └── exceptions.py    # カスタム例外
│   ├── gui/                 # ユーザーインターフェース
│   │   ├── __init__.py
│   │   └── app.py           # メインアプリケーション
│   └── utils/               # ユーティリティ
│       ├── __init__.py
│       └── logger.py        # ロギング設定
├── tests/
│   ├── __init__.py
│   └── test_config.py       # 設定管理のテスト
├── main_new.py              # アプリケーション エントリーポイント
├── config.json              # 設定ファイル（生成される）
└── README.md
```

## テストの実行

```bash
python -m pytest tests/
# または
python -m unittest discover tests
```

## アーキテクチャの改善点

### 以前のコード
- `main.py`: グローバル変数、責任混在
- `gui.py`: GUI ロジックと API 呼び出しが混在

### リファクタリング後
- **関心の分離**: 各モジュールが単一の責任を持つ
- **設定管理**: 専門的な `AppConfig`, `GameConfig` データクラス
- **API ラッパー**: `TwitchClient` による統一インターフェース
- **ロギング**: 構造化されたロギングシステム
- **エラーハンドリ**: カスタム例外による適切なエラー処理
- **テスト性**: 各コンポーネントが独立でテスト可能

## TODO

- [ ] 環境変数による認証情報の完全な外部化
- [ ] GUI フレームワークの刷新（tkinter など）
- [ ] より詳細なテストカバレッジ
- [ ] ドキュメントの英語化
- [ ] GitHub Actions による CI/CD 構築
- [ ] 実行ファイル（exe）のビルド対応

## ライセンス

MIT License

## 開発者

aliceD1540
