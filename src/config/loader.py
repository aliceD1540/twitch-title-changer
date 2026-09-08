"""設定ファイル管理"""

import json
from pathlib import Path
from typing import Optional

from .models import AppConfig
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ConfigLoader:
    """設定ファイルの読み込みと保存を管理"""

    def __init__(self, config_path: str = "./config.json"):
        """
        初期化

        Args:
            config_path: 設定ファイルのパス
        """
        self.config_path = Path(config_path)
        self.config: Optional[AppConfig] = None

    def load(self) -> AppConfig:
        """
        設定ファイルから設定を読み込む

        Returns:
            AppConfig: 読み込んだ設定

        Raises:
            FileNotFoundError: 設定ファイルが見つからない場合
            ValueError: 設定ファイルが不正な場合
        """
        try:
            if not self.config_path.exists():
                raise FileNotFoundError(f"Config file not found: {self.config_path}")

            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.config = AppConfig.from_dict(data)
            logger.info(f"Configuration loaded from {self.config_path}")
            return self.config

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            raise ValueError(f"Invalid JSON in config file: {e}")
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
            raise

    def save(self) -> None:
        """
        現在の設定をファイルに保存

        Raises:
            RuntimeError: 設定が読み込まれていない場合
        """
        if self.config is None:
            raise RuntimeError("No configuration loaded. Call load() first.")

        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config.to_dict(), f, ensure_ascii=False, indent=4)
            logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Error saving config file: {e}")
            raise

    def get_config(self) -> AppConfig:
        """
        現在の設定を取得

        Returns:
            AppConfig: 現在の設定

        Raises:
            RuntimeError: 設定が読み込まれていない場合
        """
        if self.config is None:
            raise RuntimeError("No configuration loaded. Call load() first.")
        return self.config
