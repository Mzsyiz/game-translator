#!/usr/bin/env python3
"""
模型下载脚本 - 下载 Whisper 和 Argos Translate 模型
"""
import argostranslate.package
import argostranslate.translate
from loguru import logger
import sys


def download_argos_models():
    """
    下载 Argos Translate 翻译模型
    """
    logger.info("开始下载 Argos Translate 模型...")

    # 更新包索引
    logger.info("更新包索引...")
    argostranslate.package.update_package_index()

    # 需要下载的语言对
    language_pairs = [
        ('en', 'zh'),  # 英语 -> 中文
        ('ru', 'en'),  # 俄语 -> 英语
        ('ja', 'en'),  # 日语 -> 英语
        ('ko', 'en'),  # 韩语 -> 英语
        ('fr', 'en'),  # 法语 -> 英语
        ('de', 'en'),  # 德语 -> 英语
        ('es', 'en'),  # 西班牙语 -> 英语
    ]

    # 获取可用包
    available_packages = argostranslate.package.get_available_packages()

    for from_code, to_code in language_pairs:
        logger.info(f"查找翻译包: {from_code} -> {to_code}")

        # 查找包
        package_to_install = None
        for package in available_packages:
            if package.from_code == from_code and package.to_code == to_code:
                package_to_install = package
                break

        if not package_to_install:
            logger.warning(f"未找到翻译包: {from_code} -> {to_code}")
            continue

        try:
            # 检查是否已安装
            installed = argostranslate.package.get_installed_packages()
            already_installed = any(
                p.from_code == from_code and p.to_code == to_code
                for p in installed
            )

            if already_installed:
                logger.info(f"翻译包已安装: {from_code} -> {to_code}")
                continue

            # 下载并安装
            logger.info(f"下载翻译包: {from_code} -> {to_code}...")
            download_path = package_to_install.download()

            logger.info(f"安装翻译包: {from_code} -> {to_code}...")
            argostranslate.package.install_from_path(download_path)

            logger.info(f"✓ 翻译包安装成功: {from_code} -> {to_code}")

        except Exception as e:
            logger.error(f"✗ 安装翻译包失败 ({from_code} -> {to_code}): {e}")

    logger.info("Argos Translate 模型下载完成")


def download_whisper_models():
    """
    下载 Whisper 模型（首次运行时自动下载）
    """
    logger.info("Whisper 模型将在首次运行时自动下载")
    logger.info("模型大小:")
    logger.info("  - tiny: ~75 MB")
    logger.info("  - base: ~150 MB")
    logger.info("  - small: ~500 MB")
    logger.info("  - medium: ~1.5 GB (推荐)")
    logger.info("  - large: ~3 GB")


def main():
    """
    主函数
    """
    logger.add("download_models.log", rotation="10 MB")

    logger.info("="*60)
    logger.info("模型下载工具")
    logger.info("="*60)

    try:
        # 下载 Whisper 模型说明
        download_whisper_models()

        print()

        # 下载 Argos Translate 模型
        download_argos_models()

        print()
        logger.info("="*60)
        logger.info("所有模型下载完成！")
        logger.info("="*60)

    except KeyboardInterrupt:
        logger.warning("下载被中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"下载失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
