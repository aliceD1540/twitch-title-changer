# Copyright (c) 2026 project-grimoire.dev
# Licensed under the MIT License. See LICENSE file for details.

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
    """ロケール設定を初期化（OS 別対応）"""
    if sys.platform == "win32":
        # Windows: シフトJIS または UTF-8 の試行
        try:
            locale.setlocale(locale.LC_ALL, "ja_JP")
            logger.info("Locale set to ja_JP (Windows)")
        except locale.Error:
            try:
                # Windows コンソールは既に UTF-8 に設定（run.cmd で chcp 65001）
                locale.setlocale(locale.LC_ALL, "")
                logger.info("Locale set to system default (Windows)")
            except locale.Error:
                logger.warning("Could not set locale on Windows")
    else:
        # Linux/WSL: ja_JP.UTF-8 の試行
        try:
            locale.setlocale(locale.LC_ALL, "ja_JP.UTF-8")
            logger.info("Locale set to ja_JP.UTF-8 (Linux/WSL)")
        except locale.Error:
            try:
                locale.setlocale(locale.LC_ALL, "")
                logger.info("Locale set to system default (Linux/WSL)")
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
