"""Twitch Title Changer - メインエントリーポイント"""

import asyncio
import os
import sys
from pathlib import Path

from src.gui.app import TwitchTitleChangerApp
from src.utils.logger import get_logger

logger = get_logger(__name__)


def main() -> None:
    """メインエントリーポイント"""
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
