# Copyright (c) 2026 project-grimoire.dev
# Licensed under the MIT License. See LICENSE file for details.

"""テストコード"""

import unittest
import tempfile
import json
from pathlib import Path

from src.config.models import GameConfig, AppConfig
from src.config.loader import ConfigLoader


class TestGameConfig(unittest.TestCase):
    """GameConfigのテスト"""

    def test_creation(self):
        """ゲーム設定の作成"""
        game = GameConfig(
            game_id="123",
            game_name="Test Game",
            title="Test Title",
            priority=0,
            tags="test",
        )
        self.assertEqual(game.game_id, "123")
        self.assertEqual(game.game_name, "Test Game")

    def test_to_dict(self):
        """辞書への変換"""
        game = GameConfig(
            game_id="123",
            game_name="Test Game",
            title="Test Title",
            priority=0,
            tags="test",
        )
        data = game.to_dict()
        self.assertEqual(data["GameId"], "123")
        self.assertEqual(data["GameName"], "Test Game")

    def test_from_dict(self):
        """辞書からの生成"""
        data = {
            "GameId": "123",
            "GameName": "Test Game",
            "Title": "Test Title",
            "Priority": 0,
            "Tags": "test",
        }
        game = GameConfig.from_dict(data)
        self.assertEqual(game.game_id, "123")
        self.assertEqual(game.game_name, "Test Game")


class TestAppConfig(unittest.TestCase):
    """AppConfigのテスト"""

    def test_creation(self):
        """アプリ設定の作成"""
        config = AppConfig(client_id="123", secret_id="secret")
        self.assertEqual(config.client_id, "123")
        self.assertEqual(config.secret_id, "secret")

    def test_add_game(self):
        """ゲームの追加"""
        config = AppConfig(client_id="123", secret_id="secret")
        game = GameConfig(
            game_id="456",
            game_name="Test",
            title="Test",
            priority=0,
        )
        config.add_game(game)
        self.assertEqual(len(config.games), 1)
        self.assertEqual(config.games[0].game_id, "456")

    def test_remove_game(self):
        """ゲームの削除"""
        config = AppConfig(client_id="123", secret_id="secret")
        game = GameConfig(
            game_id="456",
            game_name="Test",
            title="Test",
            priority=0,
        )
        config.add_game(game)
        config.remove_game(0)
        self.assertEqual(len(config.games), 0)

    def test_get_sorted_games(self):
        """ゲームのソート"""
        config = AppConfig(client_id="123", secret_id="secret")
        game1 = GameConfig("1", "A", "A", priority=2)
        game2 = GameConfig("2", "B", "B", priority=0)
        game3 = GameConfig("3", "C", "C", priority=1)
        config.add_game(game1)
        config.add_game(game2)
        config.add_game(game3)

        sorted_games = config.get_sorted_games()
        self.assertEqual(sorted_games[0].priority, 0)
        self.assertEqual(sorted_games[1].priority, 1)
        self.assertEqual(sorted_games[2].priority, 2)

    def test_get_max_priority(self):
        """最大優先度の取得"""
        config = AppConfig(client_id="123", secret_id="secret")
        game1 = GameConfig("1", "A", "A", priority=2)
        game2 = GameConfig("2", "B", "B", priority=5)
        config.add_game(game1)
        config.add_game(game2)

        self.assertEqual(config.get_max_priority(), 5)


class TestConfigLoader(unittest.TestCase):
    """ConfigLoaderのテスト"""

    def setUp(self):
        """テストの準備"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp_dir.name) / "config.json"

    def tearDown(self):
        """テストの後片付け"""
        self.temp_dir.cleanup()

    def test_save_and_load(self):
        """設定の保存と読み込み"""
        config = AppConfig(client_id="123", secret_id="secret")
        game = GameConfig("1", "Test", "Test", priority=0)
        config.add_game(game)

        loader = ConfigLoader(str(self.config_path))
        loader.config = config
        loader.save()

        # 新しいローダーで読み込み
        loader2 = ConfigLoader(str(self.config_path))
        loaded_config = loader2.load()

        self.assertEqual(loaded_config.client_id, "123")
        self.assertEqual(loaded_config.secret_id, "secret")
        self.assertEqual(len(loaded_config.games), 1)
        self.assertEqual(loaded_config.games[0].game_name, "Test")


if __name__ == "__main__":
    unittest.main()
