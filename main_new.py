"""Twitch Title Changer - メインエントリーポイント"""

import asyncio
import os
import sys
import locale
from pathlib import Path

from src.gui.app import TwitchTitleChangerApp
from src.utils.logger import get_logger

logger = get_logger(__name__)


def setup_locale() -> None:
    """ロケール設定を初期化（WSL/Linux での文字化け対策）"""
    try:
        # UTF-8 ロケールを設定
        locale.setlocale(locale.LC_ALL, "ja_JP.UTF-8")
        logger.info("Locale set to ja_JP.UTF-8")
    except locale.Error:
        try:
            # フォールバック: システムデフォルト
            locale.setlocale(locale.LC_ALL, "")
            logger.info("Locale set to system default")
        except locale.Error:
            logger.warning("Could not set locale, using C")


def main() -> None:
    """メインエントリーポイント"""
    # ロケール設定
    setup_locale()

    # ワーキングディレクトリを設定
    if getattr(sys, "frozen", False):
        # PyInstallerでフリーズされた場合
        working_dir = Path(sys.executable).parent
    else:
        # 通常実行の場合
        working_dir = Path(__file__).parent

    os.chdir(working_dir)
    logger.info(f"Working directory: {working_dir}")

    try:
        app = TwitchTitleChangerApp("./config.json")
        asyncio.run(app.run())
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
