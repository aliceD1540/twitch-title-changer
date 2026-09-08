"""GUI アプリケーションメイン"""

import asyncio
import locale
import tkinter as tk
import tkinter.font as tkFont
from typing import Optional, List

import PySimpleGUI as sg

from src.api.twitch_client import TwitchClient
from src.config.loader import ConfigLoader
from src.config.models import GameConfig
from src.utils.logger import get_logger

logger = get_logger(__name__)

# ロケール設定（UTF-8を確保）
try:
    locale.setlocale(locale.LC_ALL, "ja_JP.UTF-8")
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, "")
    except locale.Error:
        pass

# PySimpleGUI の日本語フォント設定
# WSL 環境での文字化け対策
_FONT_SIZE = 10
_DEFAULT_FONT = ("Noto Sans CJK JP", _FONT_SIZE)  # WSL/Linux での日本語対応フォント
_BUTTON_FONT = ("Noto Sans CJK JP", 10)
_TEXT_FONT = ("Noto Sans CJK JP", 10)

# フォントが利用できない場合のフォールバック設定
try:
    sg.set_options(font=_DEFAULT_FONT)
except Exception as e:
    # フォントが見つからない場合は、システムデフォルトを使用
    logger.warning(f"Could not set font option: {e}")
    sg.set_options(font=("TkDefaultFont", _FONT_SIZE))

sg.theme("BlueMono")


def _apply_font_to_window(window: sg.Window, font: tuple) -> None:
    """
    PySimpleGUI Window に tkinter フォント設定を適用
    タイトルバーを含む全体的なフォント設定

    Args:
        window: PySimpleGUI Window オブジェクト
        font: フォント設定 (family, size)
    """
    try:
        # PySimpleGUI Window の基になっている tkinter Window にアクセス
        root = window.TKroot
        if not root:
            return

        font_family = font[0] if isinstance(font, tuple) and len(font) > 0 else "TkDefaultFont"
        font_size = font[1] if isinstance(font, tuple) and len(font) > 1 else _FONT_SIZE

        # tkinter フォント設定を作成（ウィンドウ作成後なので安全）
        try:
            tk_font = tkFont.Font(family=font_family, size=font_size)
        except tk.TclError:
            # フォントが見つからない場合はデフォルトを使用
            tk_font = tkFont.Font(family="TkDefaultFont", size=font_size)
            logger.warning(
                f"Font '{font_family}' not found, using system default"
            )

        # ウィンドウ全体のデフォルトフォントを設定
        root.option_add("*Font", tk_font)

        # すべての子 widget に対して直接フォント設定を適用
        def set_font_recursive(widget):
            """再帰的にすべてのウィジェットにフォント設定を適用"""
            try:
                # widget がフォント属性を持つ場合は設定
                if hasattr(widget, "configure"):
                    try:
                        widget.configure(font=tk_font)
                    except tk.TclError:
                        # フォント設定が不可能なウィジェットはスキップ
                        pass
            except Exception:
                pass

            # 子ウィジェットに対して再帰的に処理
            try:
                for child in widget.winfo_children():
                    set_font_recursive(child)
            except Exception:
                pass

        # ルートウィンドウから再帰的にフォント設定を適用
        set_font_recursive(root)

    except Exception as e:
        logger.warning(f"Could not apply tkinter font: {e}")


class TwitchTitleChangerApp:
    """Twitchタイトル変更ツールのメインアプリケーション"""

    def __init__(self, config_path: str = "./config.json"):
        """
        初期化

        Args:
            config_path: 設定ファイルのパス
        """
        self.config_loader = ConfigLoader(config_path)
        self.config = None
        self.twitch_client: Optional[TwitchClient] = None
        self.main_window: Optional[sg.Window] = None

    async def initialize(self) -> bool:
        """
        アプリケーションを初期化

        Returns:
            bool: 初期化成功
        """
        try:
            # 設定を読み込む
            self.config = self.config_loader.load()
            logger.info("Configuration loaded")

            # Twitchクライアントを初期化
            self.twitch_client = TwitchClient(
                self.config.client_id, self.config.secret_id
            )
            await self.twitch_client.initialize()
            logger.info("Application initialized")
            return True

        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            sg.popup_error("初期化に失敗しました", f"{e}")
            return False

    def _create_main_layout(self) -> list:
        """メインウインドウのレイアウトを作成"""
        game_list = self._get_game_list_display()
        header = ("ゲームタイトル", "ゲームID", "配信タイトル", "タグ")

        return [
            [
                sg.Text("Twitch ユーザー名"),
                sg.InputText(
                    key="twitch_user_name",
                    default_text=self.config.twitch_user_name or "",
                ),
                sg.Button("認証"),
            ],
            [
                sg.Table(
                    game_list,
                    headings=header,
                    auto_size_columns=False,
                    col_widths=[30, 10, 50, 20],
                    justification="left",
                    key="list",
                )
            ],
            [
                sg.Column(
                    [
                        [
                            sg.Button("↑"),
                            sg.Button("↓"),
                            sg.Button("作成"),
                            sg.Button("編集"),
                            sg.Button("削除"),
                            sg.Button("Twitchに反映"),
                        ]
                    ],
                    justification="r",
                )
            ],
        ]

    def _get_game_list_display(self) -> List[List]:
        """ゲームリストを表示用フォーマットに変換"""
        game_list = []
        for game in self.config.get_sorted_games():
            game_list.append([game.game_name, game.game_id, game.title, game.tags])
        return game_list

    def _open_main_window(self) -> None:
        """メインウインドウを開く"""
        layout = self._create_main_layout()
        self.main_window = sg.Window(
            "Twitch タイトル変更ツール",
            layout,
            finalize=True,
            resizable=False,
            font=_DEFAULT_FONT,
        )
        # tkinter フォント設定を適用（タイトルバーの文字化け対策）
        _apply_font_to_window(self.main_window, _DEFAULT_FONT)

    async def _handle_authenticate(self, username: str) -> None:
        """認証処理"""
        try:
            if not username:
                sg.popup_error("ユーザー名を入力してください")
                return

            access_token, refresh_token = await self.twitch_client.authenticate(
                self.config.token, self.config.refresh_token, force_verify=True
            )
            self.config.twitch_user_name = username
            self.config.token = access_token
            self.config.refresh_token = refresh_token
            self.config_loader.save()

            sg.popup_notify("認証が完了しました")
            logger.info(f"User authenticated: {username}")

        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            sg.popup_error("認証に失敗しました", f"{e}")

    def _open_edit_game_window(
        self, game: Optional[GameConfig] = None
    ) -> Optional[GameConfig]:
        """ゲーム情報編集ウインドウを開く"""
        if game is None:
            game_name = ""
            game_id = ""
            title = ""
            tags = ""
            is_new = True
        else:
            game_name = game.game_name
            game_id = game.game_id
            title = game.title
            tags = game.tags
            is_new = False

        layout = [
            [
                sg.Text("ゲームタイトル検索"),
                sg.InputText(key="search_word"),
                sg.Button("検索"),
            ],
            [sg.HorizontalSeparator()],
            [
                sg.Column(
                    [
                        [sg.Text("ゲームタイトル")],
                        [sg.Text("ゲームID")],
                        [sg.Text("配信タイトル")],
                        [sg.Text("タグ")],
                    ]
                ),
                sg.Column(
                    [
                        [sg.InputText(game_name, disabled=True, key="game_name")],
                        [sg.InputText(game_id, disabled=True, key="game_id")],
                        [sg.InputText(title, key="title")],
                        [sg.InputText(tags, key="tags")],
                    ]
                ),
            ],
            [
                sg.Column(
                    [
                        [
                            sg.Button("現在のタグを読み込む"),
                            sg.Button("更新"),
                            sg.Button("キャンセル"),
                        ]
                    ],
                    justification="r",
                )
            ],
        ]

        window = sg.Window(
            "配信情報編集", layout, finalize=True, modal=True, font=_DEFAULT_FONT
        )
        # tkinter フォント設定を適用（タイトルバーの文字化け対策）
        _apply_font_to_window(window, _DEFAULT_FONT)

        while True:
            event, values = window.read()

            if event == "キャンセル" or event == sg.WIN_CLOSED:
                window.close()
                return None

            if event == "検索":
                if not values["search_word"]:
                    sg.popup_notify("検索ワードを入力してください")
                    continue
                selected = self._open_search_game_window(values["search_word"])
                if selected:
                    window["game_name"].update(selected[0])
                    window["game_id"].update(selected[1])

            if event == "現在のタグを読み込む":
                asyncio.run(self._load_current_tags(values))

            if event == "更新":
                if not values["game_id"]:
                    sg.popup_error("ゲームIDが設定されていません")
                    continue

                result_game = GameConfig(
                    game_id=values["game_id"],
                    game_name=values["game_name"],
                    title=values["title"],
                    tags=values["tags"],
                    priority=(
                        game.priority if game else self.config.get_max_priority() + 1
                    ),
                )
                window.close()
                return result_game

    def _open_search_game_window(self, query: str) -> Optional[tuple]:
        """ゲーム検索ウインドウを開く"""
        results = asyncio.run(self.twitch_client.search_games(query))
        if not results:
            sg.popup_error("ゲームが見つかりません")
            return None

        games = [[item["name"], item["id"]] for item in results]
        header = ("ゲームタイトル", "ID")

        layout = [
            [
                sg.Table(
                    games,
                    headings=header,
                    auto_size_columns=False,
                    col_widths=[30, 10],
                    justification="left",
                    key="game_list",
                )
            ],
            [
                sg.Column(
                    [[sg.Button("OK"), sg.Button("キャンセル")]], justification="r"
                )
            ],
        ]

        window = sg.Window(
            "ゲーム検索結果", layout, finalize=True, modal=True, font=_DEFAULT_FONT
        )
        # tkinter フォント設定を適用（タイトルバーの文字化け対策）
        _apply_font_to_window(window, _DEFAULT_FONT)

        while True:
            event, values = window.read()

            if event == "OK":
                if not values["game_list"]:
                    sg.popup_error("ゲームを選択してください")
                    continue
                selected_idx = values["game_list"][0]
                result = games[selected_idx]
                window.close()
                return tuple(result)

            if event == "キャンセル" or event == sg.WIN_CLOSED:
                window.close()
                return None

    async def _load_current_tags(self, values: dict) -> None:
        """現在のタグを読み込む"""
        try:
            if not self.config.twitch_user_name:
                sg.popup_error("Twitchユーザー名が設定されていません")
                return

            tags = await self.twitch_client.get_tags(self.config.twitch_user_name)
            self.main_window["tags"].update(",".join(tags))
            logger.info("Current tags loaded")

        except Exception as e:
            logger.error(f"Failed to load tags: {e}")
            sg.popup_error("タグの読み込みに失敗しました", f"{e}")

    async def _handle_regist_to_twitch(self, game: GameConfig) -> bool:
        """Twitchに配信情報を反映"""
        try:
            if not self.config.twitch_user_name:
                sg.popup_error("Twitchユーザー名が設定されていません")
                return False

            broadcaster_id = await self.twitch_client.get_broadcaster_id(
                self.config.twitch_user_name
            )
            tags = game.tags.split(",") if game.tags else []

            success = await self.twitch_client.update_channel_information(
                broadcaster_id=broadcaster_id,
                game_id=game.game_id,
                title=game.title,
                tags=tags,
            )

            if success:
                sg.popup_notify("配信情報をTwitchに反映しました")
                logger.info(
                    f"Channel information updated for {self.config.twitch_user_name}"
                )
            else:
                sg.popup_error("Twitchへの反映に失敗しました")

            return success

        except Exception as e:
            logger.error(f"Failed to register to Twitch: {e}")
            sg.popup_error("エラーが発生しました", f"{e}")
            return False

    def _swap_games(self, idx1: int, idx2: int) -> None:
        """ゲームの優先度を入れ替え"""
        if 0 <= idx1 < len(self.config.games) and 0 <= idx2 < len(self.config.games):
            game1 = self.config.games[idx1]
            game2 = self.config.games[idx2]
            game1.priority, game2.priority = game2.priority, game1.priority
            self.config_loader.save()
            self.main_window["list"].update(values=self._get_game_list_display())
            self.main_window["list"].update(select_rows=[idx2])

    async def run(self) -> None:
        """アプリケーションを実行"""
        if not await self.initialize():
            return

        self._open_main_window()

        while True:
            event, values = self.main_window.read()

            if event == sg.WIN_CLOSED:
                break

            if event == "認証":
                await self._handle_authenticate(values["twitch_user_name"])

            if event == "作成":
                new_game = self._open_edit_game_window()
                if new_game:
                    self.config.add_game(new_game)
                    self.config_loader.save()
                    self.main_window["list"].update(
                        values=self._get_game_list_display()
                    )

            if event == "編集":
                selected = values["list"]
                if not selected:
                    sg.popup_error("ゲームを選択してください")
                    continue
                selected_idx = selected[0]
                game_list = self.config.get_sorted_games()
                original_idx = self.config.games.index(game_list[selected_idx])
                updated_game = self._open_edit_game_window(game_list[selected_idx])
                if updated_game:
                    self.config.update_game(original_idx, updated_game)
                    self.config_loader.save()
                    self.main_window["list"].update(
                        values=self._get_game_list_display()
                    )

            if event == "削除":
                selected = values["list"]
                if not selected:
                    sg.popup_error("ゲームを選択してください")
                    continue
                if sg.popup_ok_cancel("本当に削除しますか?", title="確認") == "OK":
                    selected_idx = selected[0]
                    game_list = self.config.get_sorted_games()
                    original_idx = self.config.games.index(game_list[selected_idx])
                    self.config.remove_game(original_idx)
                    self.config_loader.save()
                    self.main_window["list"].update(
                        values=self._get_game_list_display()
                    )

            if event == "Twitchに反映":
                selected = values["list"]
                if not selected:
                    sg.popup_error("ゲームを選択してください")
                    continue
                selected_idx = selected[0]
                game_list = self.config.get_sorted_games()
                await self._handle_regist_to_twitch(game_list[selected_idx])

            if event == "↑":
                selected = values["list"]
                if selected and selected[0] > 0:
                    self._swap_games(selected[0], selected[0] - 1)

            if event == "↓":
                selected = values["list"]
                if selected and selected[0] < len(self.config.games) - 1:
                    self._swap_games(selected[0], selected[0] + 1)

        self.main_window.close()
        if self.twitch_client:
            await self.twitch_client.close()
        logger.info("Application closed")
