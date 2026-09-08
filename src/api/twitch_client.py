"""Twitch APIクライアント"""

from typing import List, Optional, Dict, Any

from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator, refresh_access_token
from twitchAPI.type import AuthScope, InvalidTokenException
from twitchAPI.helper import first

from src.utils.logger import get_logger
from .exceptions import TwitchAuthenticationError, TwitchConnectionError

logger = get_logger(__name__)


class TwitchClient:
    """Twitch APIの統一されたインターフェース"""

    def __init__(self, client_id: str, secret_id: str):
        """
        初期化

        Args:
            client_id: Twitch Client ID
            secret_id: Twitch Secret ID
        """
        self.client_id = client_id
        self.secret_id = secret_id
        self.twitch: Optional[Twitch] = None
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.target_scope = [AuthScope.CHANNEL_MANAGE_BROADCAST]

    async def initialize(self) -> None:
        """APIクライアントを初期化"""
        try:
            self.twitch = await Twitch(self.client_id, self.secret_id)
            logger.info("Twitch API client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Twitch client: {e}")
            raise TwitchConnectionError(f"Failed to initialize Twitch client: {e}")

    async def authenticate(
        self,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        force_verify: bool = False,
    ) -> tuple[str, str]:
        """
        認証処理

        Args:
            access_token: 既存のアクセストークン
            refresh_token: リフレッシュトークン
            force_verify: 強制的に再認証するか

        Returns:
            tuple: (access_token, refresh_token)

        Raises:
            TwitchAuthenticationError: 認証に失敗した場合
        """
        if not self.twitch:
            raise TwitchConnectionError("Twitch client not initialized")

        try:
            if access_token and refresh_token and not force_verify:
                # 既存のトークンを使用
                try:
                    await self.twitch.set_user_authentication(
                        access_token, self.target_scope, refresh_token
                    )
                    self.access_token = access_token
                    self.refresh_token = refresh_token
                    logger.info("Using existing access token")
                    return access_token, refresh_token
                except InvalidTokenException:
                    # トークンが無効な場合はリフレッシュ
                    logger.warning("Access token expired, refreshing...")
                    new_access_token, new_refresh_token = (
                        await self._refresh_token_impl(refresh_token)
                    )
                    await self.twitch.set_user_authentication(
                        new_access_token, self.target_scope, new_refresh_token
                    )
                    self.access_token = new_access_token
                    self.refresh_token = new_refresh_token
                    return new_access_token, new_refresh_token
            else:
                # 新規認証
                auth = UserAuthenticator(
                    self.twitch, self.target_scope, force_verify=force_verify
                )
                new_access_token, new_refresh_token = await auth.authenticate()
                await self.twitch.set_user_authentication(
                    new_access_token, self.target_scope, new_refresh_token
                )
                self.access_token = new_access_token
                self.refresh_token = new_refresh_token
                logger.info("New authentication successful")
                return new_access_token, new_refresh_token

        except InvalidTokenException as e:
            logger.error(f"Token validation failed: {e}")
            raise TwitchAuthenticationError(f"Token validation failed: {e}")
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise TwitchAuthenticationError(f"Authentication failed: {e}")

    async def _refresh_token_impl(self, refresh_token: str) -> tuple[str, str]:
        """
        トークンをリフレッシュ

        Args:
            refresh_token: リフレッシュトークン

        Returns:
            tuple: (new_access_token, new_refresh_token)

        Raises:
            TwitchAuthenticationError: リフレッシュに失敗した場合
        """
        try:
            new_access_token, new_refresh_token = refresh_access_token(
                refresh_token, self.client_id, self.secret_id
            )
            logger.info("Token refreshed successfully")
            return new_access_token, new_refresh_token
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise TwitchAuthenticationError(f"Token refresh failed: {e}")

    async def search_games(self, query: str) -> List[Dict[str, Any]]:
        """
        ゲームを検索

        Args:
            query: 検索クエリ

        Returns:
            List[Dict]: 検索結果
        """
        if not self.twitch:
            raise TwitchConnectionError("Twitch client not initialized")

        try:
            results = []
            async for item in self.twitch.search_categories(query):
                results.append(item)
            logger.info(f"Game search completed: {query}, found {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Game search failed: {e}")
            return []

    async def get_broadcaster_id(self, broadcaster_name: str) -> str:
        """
        配信者IDを取得

        Args:
            broadcaster_name: 配信者名

        Returns:
            str: 配信者ID

        Raises:
            TwitchConnectionError: 取得に失敗した場合
        """
        if not self.twitch:
            raise TwitchConnectionError("Twitch client not initialized")

        try:
            user = await first(self.twitch.get_users(logins=[broadcaster_name]))
            if user and hasattr(user, "id"):
                logger.info(f"Broadcaster ID retrieved: {broadcaster_name}")
                return user.id
            raise TwitchConnectionError(f"Broadcaster not found: {broadcaster_name}")
        except Exception as e:
            logger.error(f"Failed to get broadcaster ID: {e}")
            raise TwitchConnectionError(f"Failed to get broadcaster ID: {e}")

    async def get_channel_information(
        self, broadcaster_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        チャンネル情報を取得

        Args:
            broadcaster_id: 配信者ID

        Returns:
            Optional[Dict]: チャンネル情報
        """
        if not self.twitch:
            raise TwitchConnectionError("Twitch client not initialized")

        try:
            result = await self.twitch.get_channel_information(
                broadcaster_id=broadcaster_id
            )
            logger.info(f"Channel information retrieved for {broadcaster_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to get channel information: {e}")
            return None

    async def get_tags(self, broadcaster_name: str) -> List[str]:
        """
        チャンネルのタグを取得

        Args:
            broadcaster_name: 配信者名

        Returns:
            List[str]: タグのリスト
        """
        try:
            broadcaster_id = await self.get_broadcaster_id(broadcaster_name)
            result = await self.get_channel_information(broadcaster_id)

            if result and hasattr(result[0], "tags"):
                tags = result[0].tags
                logger.info(f"Tags retrieved for {broadcaster_name}: {tags}")
                return tags if tags else []
            return []
        except Exception as e:
            logger.error(f"Failed to get tags: {e}")
            return []

    async def update_channel_information(
        self,
        broadcaster_id: str,
        game_id: str,
        title: str,
        tags: List[str],
        language: str = "ja",
    ) -> bool:
        """
        チャンネル情報を更新

        Args:
            broadcaster_id: 配信者ID
            game_id: ゲームID
            title: 配信タイトル
            tags: タグのリスト
            language: 配信言語

        Returns:
            bool: 成功したか
        """
        if not self.twitch:
            raise TwitchConnectionError("Twitch client not initialized")

        try:
            await self.twitch.modify_channel_information(
                broadcaster_id=broadcaster_id,
                game_id=game_id,
                broadcaster_language=language,
                title=title,
                tags=tags,
            )
            logger.info(f"Channel information updated for {broadcaster_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update channel information: {e}")
            return False

    async def close(self) -> None:
        """クライアントを閉じる"""
        if self.twitch:
            await self.twitch.close()
            logger.info("Twitch client closed")
