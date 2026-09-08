"""設定データモデル"""

from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class GameConfig:
    """ゲーム配信情報"""

    game_id: str
    game_name: str
    title: str
    priority: int
    tags: str = ""

    def to_dict(self) -> dict:
        """辞書に変換"""
        return {
            "GameId": self.game_id,
            "GameName": self.game_name,
            "Title": self.title,
            "Priority": self.priority,
            "Tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GameConfig":
        """辞書から生成"""
        return cls(
            game_id=str(data.get("GameId", "")),
            game_name=data.get("GameName", ""),
            title=data.get("Title", ""),
            priority=data.get("Priority", 0),
            tags=data.get("Tags", ""),
        )


@dataclass
class AppConfig:
    """アプリケーション設定"""

    client_id: str
    secret_id: str
    twitch_user_name: Optional[str] = None
    token: Optional[str] = None
    refresh_token: Optional[str] = None
    games: List[GameConfig] = field(default_factory=list)

    def to_dict(self) -> dict:
        """辞書に変換"""
        data = {
            "ClientId": self.client_id,
            "SecretId": self.secret_id,
            "Games": [game.to_dict() for game in self.games],
        }
        if self.twitch_user_name:
            data["TwitchUserName"] = self.twitch_user_name
        if self.token:
            data["Token"] = self.token
        if self.refresh_token:
            data["RefreshToken"] = self.refresh_token
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "AppConfig":
        """辞書から生成"""
        games = [GameConfig.from_dict(game) for game in data.get("Games", [])]
        return cls(
            client_id=data.get("ClientId", ""),
            secret_id=data.get("SecretId", ""),
            twitch_user_name=data.get("TwitchUserName"),
            token=data.get("Token"),
            refresh_token=data.get("RefreshToken"),
            games=games,
        )

    def add_game(self, game: GameConfig) -> None:
        """ゲームを追加"""
        self.games.append(game)

    def remove_game(self, index: int) -> None:
        """ゲームを削除"""
        if 0 <= index < len(self.games):
            del self.games[index]

    def update_game(self, index: int, game: GameConfig) -> None:
        """ゲームを更新"""
        if 0 <= index < len(self.games):
            self.games[index] = game

    def get_sorted_games(self) -> List[GameConfig]:
        """優先度でソートされたゲームリストを取得"""
        return sorted(self.games, key=lambda x: x.priority)

    def get_max_priority(self) -> int:
        """優先度の最大値を取得"""
        if not self.games:
            return 0
        return max(game.priority for game in self.games)
