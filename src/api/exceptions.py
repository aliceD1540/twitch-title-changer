# Copyright (c) 2026 project-grimoire.dev
# Licensed under the MIT License. See LICENSE file for details.

"""Twitch API例外定義"""


class TwitchAPIError(Exception):
    """Twitch APIエラーの基底クラス"""

    pass


class TwitchAuthenticationError(TwitchAPIError):
    """認証エラー"""

    pass


class TwitchRateLimitError(TwitchAPIError):
    """レート制限エラー"""

    pass


class TwitchConnectionError(TwitchAPIError):
    """接続エラー"""

    pass
