# WSL 環境での実行ガイド

このドキュメントは、Windows Subsystem for Linux (WSL) 環境でTwitch Title Changerを実行する際の設定方法を説明します。

## WSL での文字化け（豆腐）対策

WSL で日本語が正しく表示されないことがあります。以下の手順で対応してください。

### 1. ロケール設定の確認

WSL でのロケール設定を確認します：

```bash
locale
```

出力例：
```
LANG=en_US.UTF-8
LC_CTYPE="en_US.UTF-8"
LC_NUMERIC="en_US.UTF-8"
...
```

#### 日本語ロケールが利用可能か確認

```bash
locale -a | grep ja_JP
```

出力例：
```
ja_JP.utf8
```

### 2. ロケールの設定

#### 方法 A: 環境変数で設定（推奨）

シェルの設定ファイに以下を追加します（`.bashrc`, `.zshrc` など）：

```bash
# 日本語ロケールを設定
export LANG=ja_JP.UTF-8
export LC_ALL=ja_JP.UTF-8
```

その後、シェルを再起動します：

```bash
source ~/.bashrc
```

#### 方法 B: wsl.conf で設定（WSL グローバル設定）

Windows の `%UserProfile%\.wslconfig` ファイルを編集：

```ini
[interop]
appendWindowsPath = true

[system]
locale = ja_JP.UTF-8
```

その後 WSL を再起動します。

### 3. 日本語フォントのインストール

WSL で日本語を正しく表示するには、日本語フォントが必要です。

#### Ubuntu/Debian の場合

```bash
sudo apt update
sudo apt install fonts-noto-cjk fonts-noto-cjk-extra -y
```

#### Fedora の場合

```bash
sudo dnf install google-noto-sans-cjk-fonts -y
```

### 4. PySimpleGUI の動作確認

アプリケーションを実行してみます：

```bash
python main_new.py
```

#### 文字化けが解決されない場合

以下を試してください：

**A. 環境変数を明示的に設定**

```bash
LANG=ja_JP.UTF-8 LC_ALL=ja_JP.UTF-8 python main_new.py
```

**B. Python のエンコーディングを指定**

```bash
export PYTHONIOENCODING=utf-8
python main_new.py
```

**C. 両方を組み合わせる**

```bash
LANG=ja_JP.UTF-8 LC_ALL=ja_JP.UTF-8 PYTHONIOENCODING=utf-8 python main_new.py
```

### 5. 永続的な設定（推奨）

シェルの設定ファイに以下を追加します：

```bash
# ~/.bashrc または ~/.zshrc に追加
export LANG=ja_JP.UTF-8
export LC_ALL=ja_JP.UTF-8
export PYTHONIOENCODING=utf-8
```

## X11 Forwarding を使用する場合

WSL 2 で X11 Forwarding を使用する場合、追加の設定が必要な場合があります。

### DISPLAY 環境変数の設定

```bash
# WSL 2 の場合
export DISPLAY=$(grep -m 1 nameserver /etc/resolv.conf | awk '{print $2}'):0.0
```

## トラブルシューティング

### 問題 1: "豆腐"（□）が表示される

**原因**: フォントが見つからないか、ロケール設定が不正

**解決方法**:
1. 上記のロケール設定を確認
2. 日本語フォントがインストールされているか確認
3. `locale` コマンドで `ja_JP.UTF-8` が表示されるか確認

### 問題 2: エラーメッセージが文字化けしている

**原因**: ターミナルのエンコーディング設定

**解決方法**:
```bash
export PYTHONIOENCODING=utf-8
```

### 問題 3: アプリケーション起動時にロケール関連のエラーが出る

**原因**: WSL 環境にロケールデータがない

**解決方法**:
```bash
sudo locale-gen ja_JP.UTF-8
sudo update-locale LANG=ja_JP.UTF-8
```

### 問題 4: GUI が表示されない

**原因**: X11 Forwarding の設定不足または DISPLAY 設定の問題

**解決方法**:
1. Windows で VcXsrv または Xming をインストール
2. WSL 側で DISPLAY 変数を設定
3. 以下のコマンドで X11 接続をテスト：

```bash
xclock
```

## WSL 推奨環境

正常に動作することが確認されている環境：

- **OS**: Windows 10/11
- **WSL**: WSL 2
- **ディストリビューション**: Ubuntu 20.04 以上 / Debian 11 以上
- **Python**: 3.8 以上
- **フォント**: Noto Sans CJK JP または同等の日本語対応フォント

## パフォーマンス最適化（オプション）

WSL 2 での実行が遅い場合、以下の最適化を試してください：

### 1. WSL の メモリ設定

`%UserProfile%\.wslconfig`:

```ini
[wsl2]
memory=4GB
processors=4
```

### 2. ストレージ最適化

不要なファイルを削除し、ディスク容量を確保します。

## 参考資料

- [WSL ドキュメント](https://docs.microsoft.com/ja-jp/windows/wsl/)
- [Noto Sans CJK フォント](https://github.com/google/noto-cjk)
- [PySimpleGUI ドキュメント](https://pysimplegui.readthedocs.io/)
- [Python ロケール設定](https://docs.python.org/ja/3/library/locale.html)

## サポート

WSL 固有の問題が発生した場合は、以下の情報と共に Issue を作成してください：

1. WSL のバージョン: `wsl --version`
2. ディストリビューション: `cat /etc/os-release`
3. ロケール設定: `locale`
4. インストール済みフォント: `fc-list :lang=ja`
5. エラーメッセージとログファイル
